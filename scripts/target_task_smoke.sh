#!/usr/bin/env bash
set -Eeuo pipefail
trap 'rc=$?; printf "ERROR: Target Task smoke failed at line %s (exit %s)\n" "$LINENO" "$rc" >&2; exit "$rc"' ERR

if [[ "${RUN_CLAUDE_SMOKE:-0}" != "1" ]]; then
  echo 'Refusing to spend model tokens. Re-run with RUN_CLAUDE_SMOKE=1 after owner authorization.' >&2
  exit 2
fi

command -v claude >/dev/null
command -v python3 >/dev/null
source_repo="$(git rev-parse --show-toplevel)"
source_head_before="$(git -C "$source_repo" rev-parse HEAD)"
source_status_before="$(git -C "$source_repo" status --porcelain=v1 --untracked-files=all)"
source_refs_before="$(git -C "$source_repo" show-ref | python3 -c 'import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())')"

tmp="$(mktemp -d "${TMPDIR:-/tmp}/tt-real-host-smoke.XXXXXX")"
repo="$tmp/repo"
tasks="$tmp/tasks"
task_id='tt-smoke-001'
model="${TT_SMOKE_MODEL:-haiku}"
effort="${TT_SMOKE_EFFORT:-low}"
timeout_seconds="${TT_SMOKE_TIMEOUT_SECONDS:-900}"
printf 'SMOKE_EVIDENCE_ROOT=%s\n' "$tmp"

git clone --local --no-hardlinks "$source_repo" "$repo" >/dev/null
git -C "$repo" remote remove origin 2>/dev/null || true
git -C "$repo" config user.email target-task-smoke@example.invalid
git -C "$repo" config user.name 'Target Task Smoke'
mkdir -m 700 -p "$tasks"

mission=' In this disposable repository, create hello.txt containing exactly hello, then deterministically validate the exact content. Use at least two separately accepted sealed-Plan steps. Do not access a network or any path outside the disposable repository and supplied task root.'
printf '%s' "$mission" >"$tmp/expected-mission.txt"
prompt="TT:$mission"
append_system="For this smoke only: TARGET_TASKS_ROOT is $tasks and TASK_ID is $task_id. Execute the repository Target Task workflow exactly. Use the registered target-task agents. This disposable clone has no remote. Write all run artifacts under the supplied task root and finish with terminal/receipt.json."

cd "$repo"
TARGET_TASKS_ROOT="$tasks" TARGET_TASK_ID="$task_id" \
python3 - "$timeout_seconds" "$tmp/claude-result.json" "$prompt" "$append_system" "$model" "$effort" <<'PY'
import os, subprocess, sys

timeout = int(sys.argv[1])
output = sys.argv[2]
prompt = sys.argv[3]
append_system = sys.argv[4]
model = sys.argv[5]
effort = sys.argv[6]
cmd = [
    "claude", "-p", prompt,
    "--append-system-prompt", append_system,
    "--output-format", "json",
    "--max-turns", "60",
    "--model", model,
    "--effort", effort,
    "--permission-mode", "acceptEdits",
    "--add-dir", os.environ["TARGET_TASKS_ROOT"],
    "--allowedTools",
    "Agent", "Read", "Write", "Edit", "Glob", "Grep",
    "Bash(python3:*)", "Bash(git status:*)", "Bash(git diff:*)",
    "Bash(git add:*)", "Bash(git commit:*)", "Bash(git rev-parse:*)",
    "Bash(git branch:*)", "Bash(git log:*)", "Bash(test:*)", "Bash(cat:*)",
    "--disallowedTools",
    "Bash(git push:*)", "Bash(gh:*)", "Bash(curl:*)", "Bash(wget:*)",
    "WebFetch", "WebSearch",
]
with open(output, "wb") as stream:
    completed = subprocess.run(cmd, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout, check=False)
if completed.returncode != 0:
    raise SystemExit(completed.returncode)
PY

python3 scripts/validate_target_task_smoke.py \
  --tasks-root "$tasks" \
  --task-id "$task_id" \
  --expected-mission-file "$tmp/expected-mission.txt" \
  --claude-result "$tmp/claude-result.json" \
  >"$tmp/smoke-validation.json"

test "$(git -C "$source_repo" rev-parse HEAD)" = "$source_head_before"
test "$(git -C "$source_repo" status --porcelain=v1 --untracked-files=all)" = "$source_status_before"
test "$(git -C "$source_repo" show-ref | python3 -c 'import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())')" = "$source_refs_before"
test -z "$(git -C "$repo" remote)"
cat "$tmp/smoke-validation.json"
printf 'REAL_HOST_SMOKE_RESULT=%s\nTASKS_ROOT=%s\n' "$tmp/claude-result.json" "$tasks"

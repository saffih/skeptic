#!/usr/bin/env bash
set -Eeuo pipefail
trap 'rc=$?; printf "ERROR: Target Task smoke failed at line %s (exit %s)\n" "$LINENO" "$rc" >&2; exit "$rc"' ERR

if [[ "${RUN_CLAUDE_SMOKE:-0}" != "1" ]]; then
  echo 'Refusing to spend model tokens. Re-run with RUN_CLAUDE_SMOKE=1 after owner authorization.' >&2
  exit 2
fi
command -v claude >/dev/null
command -v python3 >/dev/null
command -v git >/dev/null

source_repo="$(git rev-parse --show-toplevel)"
source_head_before="$(git -C "$source_repo" rev-parse HEAD)"
source_status_before="$(git -C "$source_repo" status --porcelain=v1 --untracked-files=all)"
source_refs_before="$(git -C "$source_repo" show-ref)"
source_refs_hash_before="$(printf '%s' "$source_refs_before" | shasum -a 256 | awk '{print $1}')"

tmp="$(mktemp -d "${TMPDIR:-/tmp}/tt-real-host-smoke.XXXXXX")"
repo="$tmp/repo"
tasks="$tmp/tasks"
remote="$tmp/remote.git"
task_id='tt-smoke-001'
model="${TT_SMOKE_MODEL:-haiku}"
effort="${TT_SMOKE_EFFORT:-low}"
timeout_seconds="${TT_SMOKE_TIMEOUT_SECONDS:-900}"
max_budget="${TT_SMOKE_MAX_BUDGET_USD:-1.00}"
printf 'SMOKE_EVIDENCE_ROOT=%s\n' "$tmp"

git clone --local --no-hardlinks "$source_repo" "$repo" >/dev/null
git -C "$repo" remote remove origin 2>/dev/null || true
git init --bare "$remote" >/dev/null
git -C "$repo" branch -M main
git -C "$repo" remote add smoke-local "$remote"
git -C "$repo" config user.email target-task-smoke@example.invalid
git -C "$repo" config user.name 'Target Task Smoke'
mkdir -m 700 -p "$tasks"

settings="$tmp/settings.json"
mcp_config="$tmp/empty-mcp.json"
python3 - "$settings" "$repo" "$tasks" <<'PY'
import json, sys
settings, repo, tasks = sys.argv[1:]
json.dump({
    "permissions": {
        "allow": [
            f"Read({repo}/**)", f"Read({tasks}/**)", f"Write({repo}/**)", f"Write({tasks}/**)",
            f"Edit({repo}/**)", f"Edit({tasks}/**)", f"Glob({repo}/**)", f"Glob({tasks}/**)",
            f"Grep({repo}/**)", f"Grep({tasks}/**)", "Bash(python3:*)", "Bash(git status:*)",
            "Bash(git diff:*)", "Bash(git add:*)", "Bash(git commit:*)", "Bash(git rev-parse:*)",
            "Bash(git branch:*)", "Bash(git log:*)", "Bash(git push smoke-local main:main)", "Bash(test:*)", "Bash(cat:*)",
        ],
        "deny": [
            "Bash(git push --force*)", "Bash(git push origin:*)", "Bash(git push https:*)", "Bash(git push git@*:*)", "Bash(git remote add origin:*)", "Bash(curl:*)", "Bash(wget:*)",
            "Bash(ssh:*)", "Bash(scutil:*)", "Bash(networksetup:*)", "WebFetch", "WebSearch",
            "Read(~/.ssh/**)", "Read(~/.aws/**)", "Read(~/.config/gcloud/**)", "Read(~/.netrc)",
            "Write(~/.ssh/**)", "Write(~/.aws/**)", "Write(~/.config/gcloud/**)", "Write(~/.netrc)",
            "Edit(~/.ssh/**)", "Edit(~/.aws/**)", "Edit(~/.config/gcloud/**)", "Edit(~/.netrc)",
        ],
        "defaultMode": "dontAsk",
    },
    "sandbox": {
        "enabled": True, "failIfUnavailable": True, "allowUnsandboxedCommands": False,
        "filesystem": {"allowWrite": [repo, tasks]},
        "network": {"allowedDomains": []},
    },
}, open(settings, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PY
printf '{}\n' >"$mcp_config"

mission=' In this disposable repository, create hello.txt containing exactly hello, then deterministically validate the exact content. Use at least two separately accepted sealed-Plan steps. Push only main to the supplied local smoke remote, never force-push, and do not access a network or any path outside the disposable repository and supplied task root.'
printf '%s' "$mission" >"$tmp/expected-mission.txt"
prompt="TT:$mission"
append_system="For this smoke only: TARGET_TASKS_ROOT is $tasks and TASK_ID is $task_id. The disposable repository is $repo and its only remote is the local bare repository $remote named smoke-local. Execute the repository Target Task workflow exactly. Use the registered target-task agents. Write all run artifacts under the supplied task root, finish CLOSED with terminal/receipt.json, and push only main to smoke-local without force. No network or original remote is permitted."

cd "$repo"
TARGET_TASKS_ROOT="$tasks" TARGET_TASK_ID="$task_id" CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1 CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1 \
python3 - "$timeout_seconds" "$tmp/claude-stream.jsonl" "$tmp/claude-stderr.log" "$tmp/claude-metadata.json" "$prompt" "$append_system" "$model" "$effort" "$settings" "$mcp_config" "$tasks" <<'PY'
import json, os, subprocess, sys

timeout, stream_path, stderr_path, metadata_path, prompt, append_system, model, effort, settings, mcp, tasks = sys.argv[1:]
cmd = [
    "claude", "-p", prompt, "--append-system-prompt", append_system,
    "--output-format", "stream-json", "--verbose", "--max-turns", "60",
    "--max-budget-usd", os.environ.get("TT_SMOKE_MAX_BUDGET_USD", "1.00"),
    "--model", model, "--effort", effort, "--permission-mode", "dontAsk",
    "--settings", settings, "--strict-mcp-config", "--mcp-config", mcp,
    "--disable-slash-commands", "--no-session-persistence", "--add-dir", tasks,
    "--tools", "Agent", "Read", "Write", "Edit", "Glob", "Grep", "Bash",
    "--allowedTools", "Agent(target-task-planner)", "Agent(target-task-reviewer)", "Agent(target-task-worker)",
    "Read", "Write", "Edit", "Glob", "Grep", "Bash",
    "--disallowedTools", "WebFetch", "WebSearch", "Bash(curl:*)", "Bash(wget:*)", "Bash(ssh:*)",
]
timed_out = False
with open(stream_path, "wb") as stream, open(stderr_path, "wb") as stderr:
    try:
        completed = subprocess.run(cmd, stdout=stream, stderr=stderr, timeout=int(timeout), check=False)
        exit_status = completed.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_status = 124
        if exc.stdout:
            stream.write(exc.stdout if isinstance(exc.stdout, bytes) else exc.stdout.encode())
        if exc.stderr:
            stderr.write(exc.stderr if isinstance(exc.stderr, bytes) else exc.stderr.encode())
metadata = {"exit_status": exit_status, "timed_out": timed_out, "max_budget_usd": os.environ.get("TT_SMOKE_MAX_BUDGET_USD", "1.00"), "stream_path": stream_path, "stderr_path": stderr_path}
cost_metadata = []
for raw in open(stream_path, "rb"):
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        continue
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            found = {key: item[key] for key in ("total_cost_usd", "cost_usd", "usage") if key in item}
            if found:
                cost_metadata.append(found)
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
metadata["cost_metadata"] = cost_metadata
with open(metadata_path, "w", encoding="utf-8") as output:
    json.dump(metadata, output, sort_keys=True, separators=(",", ":")); output.write("\n")
raise SystemExit(0)
PY

git -C "$repo" push smoke-local main:main >/dev/null
python3 scripts/validate_target_task_smoke.py \
  --tasks-root "$tasks" --task-id "$task_id" \
  --expected-mission-file "$tmp/expected-mission.txt" \
  --claude-result "$tmp/claude-stream.jsonl" --claude-metadata "$tmp/claude-metadata.json" \
  --source-repo "$repo" --local-remote "$remote" >"$tmp/smoke-validation.json"

test "$(git -C "$source_repo" rev-parse HEAD)" = "$source_head_before"
test "$(git -C "$source_repo" status --porcelain=v1 --untracked-files=all)" = "$source_status_before"
source_refs_after="$(git -C "$source_repo" show-ref)"
source_refs_hash_after="$(printf '%s' "$source_refs_after" | shasum -a 256 | awk '{print $1}')"
test "$source_refs_hash_after" = "$source_refs_hash_before"
cat "$tmp/smoke-validation.json"
printf 'REAL_HOST_SMOKE_RESULT=%s\nTASKS_ROOT=%s\n' "$tmp/claude-stream.jsonl" "$tasks"

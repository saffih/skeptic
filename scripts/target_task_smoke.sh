#!/usr/bin/env bash
set -Eeuo pipefail
trap 'rc=$?; printf "ERROR: Target Task smoke failed at line %s (exit %s)\n" "$LINENO" "$rc" >&2; exit "$rc"' ERR

if [[ "${RUN_CLAUDE_SMOKE:-0}" != "1" ]]; then
  echo 'Refusing to spend model tokens. Re-run with RUN_CLAUDE_SMOKE=1 after owner authorization.' >&2
  exit 2
fi

command -v claude >/dev/null
source_repo="$(git rev-parse --show-toplevel)"
source_head_before="$(git -C "$source_repo" rev-parse HEAD)"
source_status_before="$(git -C "$source_repo" status --porcelain=v1)"
source_refs_before="$(git -C "$source_repo" show-ref | sha256sum | awk '{print $1}')"

tmp="$(mktemp -d "${TMPDIR:-/tmp}/tt-real-host-smoke.XXXXXX")"
printf 'SMOKE_EVIDENCE_ROOT=%s\n' "$tmp"

git clone --local --no-hardlinks "$source_repo" "$tmp/repo" >/dev/null
git -C "$tmp/repo" remote remove origin 2>/dev/null || true
mkdir -p "$tmp/tasks"

prompt='TT: In this disposable repository, create hello.txt containing exactly hello, then run a deterministic check proving the exact file content. Use two separately accepted steps and return only the compact terminal receipt.'

(
  cd "$tmp/repo"
  TARGET_TASKS_ROOT="$tmp/tasks" \
  claude -p "$prompt" \
    --output-format json \
    --max-turns 40 \
    --permission-mode acceptEdits \
    --allowedTools Read Write Edit Glob Grep \
      'Bash(python3:*)' 'Bash(git status:*)' 'Bash(git diff:*)' \
      'Bash(git add:*)' 'Bash(git commit:*)' 'Bash(test:*)' 'Bash(cat:*)' \
    --disallowedTools \
      'Bash(git push:*)' 'Bash(gh:*)' 'Bash(curl:*)' 'Bash(wget:*)' \
      WebFetch WebSearch \
    >"$tmp/claude-result.json"
)

test "$(git -C "$source_repo" rev-parse HEAD)" = "$source_head_before"
test "$(git -C "$source_repo" status --porcelain=v1)" = "$source_status_before"
test "$(git -C "$source_repo" show-ref | sha256sum | awk '{print $1}')" = "$source_refs_before"
test -z "$(git -C "$tmp/repo" remote)"
test -s "$tmp/claude-result.json"

printf 'REAL_HOST_SMOKE_RESULT=%s\nTASKS_ROOT=%s\n' "$tmp/claude-result.json" "$tmp/tasks"

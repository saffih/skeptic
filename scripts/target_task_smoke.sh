#!/usr/bin/env bash
set -Eeuo pipefail
trap 'rc=$?; printf "target_task_smoke failed rc=%s line=%s\n" "$rc" "$LINENO" >&2; exit "$rc"' ERR
python3 -m compileall -q concepts/stt adapters scripts tests/concepts/stt
python3 -m unittest discover -s tests/concepts/stt -t .
python3 scripts/generic_host_smoke.py
python3 scripts/probe_stt_sandbox.py
python3 scripts/verify_stt_reachability.py

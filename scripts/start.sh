#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ -x .venv/bin/python ]] || { echo 'Run bash scripts/setup.sh first.' >&2; exit 1; }
.venv/bin/python -m uvicorn service:app --app-dir ai --host 127.0.0.1 --port 8091 &
ai_pid=$!
trap 'kill "$ai_pid" "${api_pid:-}" 2>/dev/null || true' EXIT
 dotnet run --project backend -c Release --no-build --no-launch-profile --urls http://127.0.0.1:5082 &
api_pid=$!
.venv/bin/python scripts/readiness.py
printf 'TajerOS is ready at http://127.0.0.1:5082\n'
wait -n "$ai_pid" "$api_pid"

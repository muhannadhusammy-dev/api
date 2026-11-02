#!/usr/bin/env bash
set -euo pipefail
root_dir="$(cd "$(dirname "$0")/.." && pwd)"
python - <<'CHECK_PORTS'
import socket
for port in (5082,8091):
    with socket.socket() as sock:
        try: sock.bind(('127.0.0.1',port))
        except OSError: raise SystemExit(f'Port {port} is in use. Stop your local stack before integration testing.')
CHECK_PORTS
test_dir="$(mktemp -d)"
python -m uvicorn service:app --app-dir "$root_dir/ai" --host 127.0.0.1 --port 8091 > "$test_dir/ai.log" 2>&1 &
ai_pid=$!
DEMO_PASSWORD="TajerDemo!2026" ConnectionStrings__Postgres="" ConnectionStrings__Sqlite="Data Source=$test_dir/test.db" dotnet run --project "$root_dir/backend" --urls http://127.0.0.1:5082 > "$test_dir/api.log" 2>&1 &
api_pid=$!
trap 'kill "$ai_pid" "$api_pid" 2>/dev/null || true; echo "Test logs: $test_dir"' EXIT
python - <<'PY'
import urllib.request,time
for url in ['http://127.0.0.1:8091/health','http://127.0.0.1:5082/api/health']:
 for _ in range(120):
  try:urllib.request.urlopen(url);break
  except Exception:time.sleep(.5)
 else:raise RuntimeError('Server did not start: '+url)
PY
python "$root_dir/tests/integration.py"

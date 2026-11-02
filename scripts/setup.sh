#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v dotnet >/dev/null || { echo 'Install the .NET 10 SDK first.' >&2; exit 1; }
command -v tesseract >/dev/null || { echo 'Install Tesseract OCR first.' >&2; exit 1; }
command -v ffmpeg >/dev/null || { echo 'Install FFmpeg first.' >&2; exit 1; }
python3 -m venv .venv
.venv/bin/python -m pip install -r ai/requirements-runtime.txt -r llm_streamlit/requirements.txt
(cd frontend && npm ci && npm run build)
dotnet build backend -c Release
echo 'Setup complete. Run bash scripts/start.sh or bash scripts/dashboard.sh.'

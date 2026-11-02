$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
foreach ($tool in @('dotnet','tesseract','ffmpeg','node')) { Get-Command $tool -ErrorAction Stop | Out-Null }
py -3.12 -m venv .venv
if ($LASTEXITCODE) { throw 'Python 3.12 venv creation failed' }
& .\.venv\Scripts\python.exe -m pip install -r ai/requirements-runtime.txt -r llm_streamlit/requirements.txt
if ($LASTEXITCODE) { throw 'Python installation failed' }
Push-Location frontend
try {
    npm ci
    if ($LASTEXITCODE) { throw 'npm ci failed' }
    npm run build
    if ($LASTEXITCODE) { throw 'UI build failed' }
} finally { Pop-Location }
dotnet build backend -c Release
if ($LASTEXITCODE) { throw '.NET build failed' }
Write-Host 'Setup complete. Run powershell -File scripts/start.ps1'

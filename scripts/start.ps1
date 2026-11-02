$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$ai = Start-Process -PassThru -NoNewWindow .\.venv\Scripts\python.exe -ArgumentList '-m','uvicorn','service:app','--app-dir','ai','--host','127.0.0.1','--port','8091'
try {
    $api = Start-Process -PassThru -NoNewWindow dotnet -ArgumentList 'run','--project','backend','-c','Release','--no-build','--no-launch-profile','--urls','http://127.0.0.1:5082'
    & .\.venv\Scripts\python.exe scripts/readiness.py
    if ($LASTEXITCODE) { throw 'Startup checks failed' }
    Write-Host 'Open http://127.0.0.1:5082. Ctrl+C stops both services.'
    while (!$ai.HasExited -and !$api.HasExited) { Start-Sleep -Seconds 1 }
} finally {
    if (!$ai.HasExited) { Stop-Process -Id $ai.Id }
    if ($api -and !$api.HasExited) { Stop-Process -Id $api.Id }
}

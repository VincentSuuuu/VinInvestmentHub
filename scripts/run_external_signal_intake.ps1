$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Python = "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$LogDir = Join-Path $ProjectRoot "logs\external-signals"
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$StdoutLog = Join-Path $LogDir "$Stamp.json"
$StderrLog = Join-Path $LogDir "$Stamp.err.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

Push-Location $ProjectRoot
try {
    & $Python scripts\fetch_external_signals.py `
        --source all `
        --write-notion `
        --json `
        --limit-per-feed 8 `
        --max-age-days 30 `
        --max-candidates 5 `
        --refresh-existing-candidates `
        --request-timeout 10 `
        2> $StderrLog |
        Set-Content -Path $StdoutLog -Encoding UTF8

    if ($LASTEXITCODE -ne 0) {
        throw "External signal intake failed with exit code $LASTEXITCODE. See $StderrLog"
    }
}
finally {
    Pop-Location
}

Write-Output "External signal intake completed. Output: $StdoutLog"

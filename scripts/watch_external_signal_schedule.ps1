$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Runner = Join-Path $PSScriptRoot "run_external_signal_intake.ps1"
$StateDir = Join-Path $ProjectRoot "logs\external-signals"
$StatePath = Join-Path $StateDir "schedule-state.json"
$Slots = @(
    @{ Name = "morning"; Start = "08:30"; End = "10:30" },
    @{ Name = "evening"; Start = "20:30"; End = "22:30" }
)

New-Item -ItemType Directory -Force -Path $StateDir | Out-Null

function Read-State {
    if (-not (Test-Path $StatePath)) {
        return @{}
    }
    $raw = Get-Content -Raw -Path $StatePath
    if (-not $raw.Trim()) {
        return @{}
    }
    $state = @{}
    (ConvertFrom-Json $raw).PSObject.Properties | ForEach-Object {
        $state[$_.Name] = $_.Value
    }
    return $state
}

function Write-State($state) {
    $state | ConvertTo-Json | Set-Content -Path $StatePath -Encoding UTF8
}

while ($true) {
    try {
        $now = Get-Date
        $today = $now.ToString("yyyy-MM-dd")
        $state = Read-State

        foreach ($slot in $Slots) {
            $start = [datetime]::ParseExact("$today $($slot.Start)", "yyyy-MM-dd HH:mm", $null)
            $end = [datetime]::ParseExact("$today $($slot.End)", "yyyy-MM-dd HH:mm", $null)
            $key = "$today-$($slot.Name)"

            if ($now -ge $start -and $now -lt $end -and $state[$key] -ne "done") {
                & $Runner
                $state[$key] = "done"
                Write-State $state
            }
        }
    }
    catch {
        $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $_ | Out-String | Set-Content -Path (Join-Path $StateDir "$stamp.scheduler.err.log") -Encoding UTF8
    }

    Start-Sleep -Seconds 60
}

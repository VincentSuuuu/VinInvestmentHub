$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Runner = Join-Path $PSScriptRoot "run_external_signal_intake.ps1"

if (-not (Test-Path $Runner)) {
    throw "Missing runner script: $Runner"
}

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Runner`""
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

$tasks = @(
    @{
        Name = "VinInvestmentHub Raw Signals Morning"
        At = "08:30"
        Description = "Phase 6 morning external news intake into Notion Raw Signals, max 5 candidates."
    },
    @{
        Name = "VinInvestmentHub Raw Signals Evening"
        At = "20:30"
        Description = "Phase 6 evening external news intake into Notion Raw Signals, max 5 candidates."
    }
)

foreach ($task in $tasks) {
    $existing = Get-ScheduledTask -TaskName $task.Name -ErrorAction SilentlyContinue
    if ($existing) {
        Unregister-ScheduledTask -TaskName $task.Name -Confirm:$false
    }

    $trigger = New-ScheduledTaskTrigger -Daily -At $task.At
    Register-ScheduledTask `
        -TaskName $task.Name `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description $task.Description | Out-Null
}

Get-ScheduledTask -TaskName "VinInvestmentHub Raw Signals Morning", "VinInvestmentHub Raw Signals Evening" |
    Select-Object TaskName, State

$ErrorActionPreference = "Stop"

$SchedulerInstaller = Join-Path $PSScriptRoot "install_external_signal_schedule.ps1"
$WatcherInstaller = Join-Path $PSScriptRoot "install_external_signal_watcher.ps1"

try {
    $schedulerResult = & $SchedulerInstaller
    [ordered]@{
        mode = "windows_task_scheduler"
        ok = $true
        detail = $schedulerResult
    } | ConvertTo-Json -Depth 4
}
catch {
    $schedulerError = $_ | Out-String
    $watcherResult = & $WatcherInstaller | ConvertFrom-Json
    [ordered]@{
        mode = "user_watcher_fallback"
        ok = $true
        scheduler_error = $schedulerError.Trim()
        watcher = $watcherResult
    } | ConvertTo-Json -Depth 6
}

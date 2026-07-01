$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Watcher = Join-Path $PSScriptRoot "watch_external_signal_schedule.ps1"
$RunKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$RunName = "VinInvestmentHubRawSignalsWatcher"
$Command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Watcher`""
$StartupDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$StartupShortcut = Join-Path $StartupDir "VinInvestmentHubRawSignalsWatcher.lnk"

if (-not (Test-Path $Watcher)) {
    throw "Missing watcher script: $Watcher"
}

$installMode = "registry_run_key"
try {
    New-Item -Path $RunKey -Force | Out-Null
    Set-ItemProperty -Path $RunKey -Name $RunName -Value $Command
}
catch {
    $installMode = "startup_folder"
    New-Item -ItemType Directory -Force -Path $StartupDir | Out-Null
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($StartupShortcut)
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Watcher`""
    $shortcut.WorkingDirectory = $ProjectRoot.Path
    $shortcut.Save()
    if (-not (Test-Path $StartupShortcut)) {
        $installMode = "current_session_only"
    }
}

$existing = Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -like "*watch_external_signal_schedule.ps1*" }

if (-not $existing) {
    Start-Process `
        -FilePath "powershell.exe" `
        -ArgumentList "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Watcher`"" `
        -WindowStyle Hidden
}

$startupShortcutExists = Test-Path $StartupShortcut
$registryValue = $null
try {
    $registryValue = (Get-ItemProperty -Path $RunKey -Name $RunName -ErrorAction Stop).$RunName
}
catch {
    $registryValue = $null
}

[ordered]@{
    mode = "user_watcher"
    install_mode = $installMode
    project_root = $ProjectRoot.Path
    run_key = $RunKey
    run_name = $RunName
    startup_shortcut = $StartupShortcut
    startup_shortcut_exists = $startupShortcutExists
    registry_value_exists = [bool]$registryValue
    persistent = [bool]$registryValue -or $startupShortcutExists
    command = $Command
    already_running = [bool]$existing
    installed_at = (Get-Date).ToString("o")
} | ConvertTo-Json

$ErrorActionPreference = "Stop"

$AppId = "3dp-cost-calculator"
$AppName = "3DP Cost Calculator"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$SourceExe = Join-Path $RepoRoot "dist\$AppId.exe"
$InstallDir = Join-Path $env:LOCALAPPDATA $AppName
$InstallExe = Join-Path $InstallDir "$AppId.exe"

if (-not (Test-Path $SourceExe)) {
    throw "Missing $SourceExe. Build it first with PyInstaller."
}

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item -Force $SourceExe $InstallExe

$ProgramsDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$StartMenuShortcut = Join-Path $ProgramsDir "$AppName.lnk"
$DesktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "$AppName.lnk"

$Shell = New-Object -ComObject WScript.Shell

foreach ($ShortcutPath in @($StartMenuShortcut, $DesktopShortcut)) {
    $Shortcut = $Shell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $InstallExe
    $Shortcut.WorkingDirectory = $InstallDir
    $Shortcut.IconLocation = "$InstallExe,0"
    $Shortcut.Description = "Calculate 3D print pricing and export receipts"
    $Shortcut.Save()
}

Write-Host "Installed $AppName to $InstallDir and created Start Menu and Desktop shortcuts."

# Waits for SlayTheSpire2 to exit, then removes ContentMod from the game's mods folder.
param([int]$StartTimeout = 120)

$modName = "ContentMod"

function Get-Sts2ModsPath {
    try {
        $props = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 2868840" -ErrorAction Stop
        if ($props.InstallLocation -and (Test-Path $props.InstallLocation)) {
            return Join-Path $props.InstallLocation "mods"
        }
    } catch {}
    try {
        $steam = Get-ItemProperty "HKCU:\Software\Valve\Steam" -ErrorAction Stop
        $sts2 = Join-Path $steam.SteamPath "steamapps/common/Slay the Spire 2"
        if (Test-Path $sts2) { return Join-Path $sts2 "mods" }
    } catch {}
    return $null
}

$modsPath = Get-Sts2ModsPath
if (-not $modsPath) { Write-Error "Could not find STS2 mods folder."; exit 1 }
$modDir = Join-Path $modsPath $modName

Write-Host "Waiting for SlayTheSpire2 to start (timeout: ${StartTimeout}s)..."
$elapsed = 0; $proc = $null
do {
    Start-Sleep 2; $elapsed += 2
    $proc = Get-Process "SlayTheSpire2" -ErrorAction SilentlyContinue
} until ($proc -or $elapsed -ge $StartTimeout)

if (-not $proc) { Write-Host "Game did not start. Nothing to clean up."; exit 0 }

Write-Host "Game running (PID $($proc.Id)). Waiting for exit..."
try { $proc.WaitForExit() } catch {}
Write-Host "Game exited."

if (Test-Path $modDir) {
    Remove-Item $modDir -Recurse -Force
    Write-Host "Removed '$modName' from mods folder."
} else {
    Write-Host "'$modName' not found in mods folder; nothing to remove."
}

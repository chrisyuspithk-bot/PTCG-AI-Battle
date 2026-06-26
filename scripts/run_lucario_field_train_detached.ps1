# Detached Lucario field train - survives closing Cursor/terminal.
# Logs append to work/train.log; PID in work/train.pid; resume via checkpoint.json.
#
#   powershell -File scripts/run_lucario_field_train_detached.ps1
#   powershell -File scripts/run_lucario_field_train_detached.ps1 -Work rl_mcts_field/lucarioex_v3_fresh

param(
    [int]$Cycles = 25,
    [string]$Work = 'rl_mcts_field/lucarioex_v4_field',
    [double]$LeverBlend = 0.45,
    [switch]$NoAutoResume
)

$ErrorActionPreference = 'Stop'
$Repo = Split-Path $PSScriptRoot -Parent
Set-Location $Repo

$python = 'C:\Users\tobin\AppData\Local\Programs\Python\Python313\python.exe'
if (-not (Test-Path $python)) {
    Write-Error "Python 3.13 not found at $python"
}

$workDir = Join-Path $Repo $Work
New-Item -ItemType Directory -Force -Path $workDir | Out-Null
$log = Join-Path $workDir 'train.log'
$launcherLog = Join-Path $workDir 'launcher.log'

function Log-Launcher([string]$Msg) {
    $line = "$(Get-Date -Format o) $Msg"
    Add-Content -Path $launcherLog -Value $line
    Write-Host $line
}

Log-Launcher "bootstrap official agents..."
& $python scripts/bootstrap_official_rule_agents.py 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "bootstrap_official_rule_agents.py failed"
}

Log-Launcher "verify official opponents..."
& $python scripts/verify_official_opponents.py 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "verify_official_opponents.py failed"
}

$ckpt = Join-Path $workDir 'checkpoint.json'
if ($NoAutoResume) {
    if (Test-Path $ckpt) { Remove-Item $ckpt -Force }
    Get-ChildItem $workDir -Filter 'model*.pth' -ErrorAction SilentlyContinue | Remove-Item -Force
    Log-Launcher "fresh run: cleared checkpoint and model*.pth"
}

$resumeArgs = @()
if (-not $NoAutoResume) {
    $resumeArgs = @('--auto-resume')
} else {
    $resumeArgs = @('--no-auto-resume')
}

$trainScript = Join-Path $Repo 'scripts\train_lucario_field_mcts.py'
$argList = @(
    '-u', $trainScript,
    '--device', 'cuda',
    '--cycles', "$Cycles",
    '--work', $Work,
    '--opponent-brain', 'native',
    '--eval-opponent', 'native',
    '--mirror-brain', 'none',
    '--gate-mode', 'field',
    '--gate-winrate', '0',
    '--games-per-opponent', '30',
    '--search-count', '20',
    '--lever-blend', "$LeverBlend",
    '--lucario-mirror-games', '20',
    '--lucario-game-mult', '1'
) + $resumeArgs

$argStr = ($argList | ForEach-Object {
    if ($_ -match '\s') { "`"$_`"" } else { $_ }
}) -join ' '

$cmdPath = Join-Path $workDir 'run_train.cmd'
$cmd = @"
@echo off
cd /d "$Repo"
echo.>> "$log"
echo ===== train start %DATE% %TIME% =====>> "$log"
"$python" $argStr >> "$log" 2>&1
echo ===== train exit %ERRORLEVEL% %DATE% %TIME% =====>> "$log"
"@
Set-Content -Path $cmdPath -Value $cmd -Encoding ASCII

Log-Launcher "starting detached: $Work ($Cycles cycles)"
$p = Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $cmdPath -WorkingDirectory $Repo -WindowStyle Hidden -PassThru
$p.Id | Set-Content -Path (Join-Path $workDir 'train.pid')
Log-Launcher "PID $($p.Id) | log: $log"
Log-Launcher "resume: powershell -File scripts/run_lucario_field_train_detached.ps1 -Work $Work"
Write-Host ""
Write-Host "Training detached. Safe to close Cursor."
Write-Host "  tail log:  Get-Content $log -Wait -Tail 30"
Write-Host "  checkpoint: $ckpt"
Write-Host "  stop:      Stop-Process -Id $($p.Id)"

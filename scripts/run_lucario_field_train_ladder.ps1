# Field-only Lucario RL+MCTS — official kiyotah pilots, no mirror, field gate.
# Detached; safe to close Cursor.
#
#   powershell -File scripts/run_lucario_field_train_ladder.ps1

param(
    [int]$Cycles = 25,
    [string]$Work = 'rl_mcts_field/lucarioex_v4_field',
    [double]$LeverBlend = 0.45,
    [int]$GamesPerOpponent = 30,
    [int]$SearchCount = 20,
    [string]$Device = 'cuda',
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

# Stop prior run in this work dir if still alive
$pidFile = Join-Path $workDir 'train.pid'
if (Test-Path $pidFile) {
    $oldPid = Get-Content $pidFile -ErrorAction SilentlyContinue
    if ($oldPid) {
        Stop-Process -Id $oldPid -Force -ErrorAction SilentlyContinue
        Log-Launcher "stopped old PID $oldPid"
    }
}

Log-Launcher "bootstrap + verify official pilots..."
& $python scripts/bootstrap_official_rule_agents.py 2>&1 | Out-Null
& $python scripts/verify_official_opponents.py 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "verify_official_opponents.py failed"
}

$ckpt = Join-Path $workDir 'checkpoint.json'
if ($NoAutoResume) {
    if (Test-Path $ckpt) { Remove-Item $ckpt -Force }
    Get-ChildItem $workDir -Filter 'model*.pth' -ErrorAction SilentlyContinue | Remove-Item -Force
    Log-Launcher "fresh run: cleared checkpoints"
}

$resumeArgs = if ($NoAutoResume) { @('--no-auto-resume') } else { @('--auto-resume') }

$trainScript = Join-Path $Repo 'scripts\train_lucario_field_mcts.py'
$argList = @(
    '-u', $trainScript,
    '--device', $Device,
    '--cycles', "$Cycles",
    '--work', $Work,
    '--opponent-brain', 'native',
    '--eval-opponent', 'native',
    '--mirror-brain', 'none',
    '--gate-mode', 'field',
    '--gate-winrate', '0',
    '--games-per-opponent', "$GamesPerOpponent",
    '--search-count', "$SearchCount",
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
echo ===== ladder field train %DATE% %TIME% =====>> "$log"
"$python" $argStr >> "$log" 2>&1
echo ===== exit %ERRORLEVEL% %DATE% %TIME% =====>> "$log"
"@
Set-Content -Path $cmdPath -Value $cmd -Encoding ASCII

Log-Launcher "starting: $Work | field + lucario mirror pilot | device=$Device"
$p = Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $cmdPath -WorkingDirectory $Repo -WindowStyle Hidden -PassThru
$p.Id | Set-Content -Path $pidFile
Log-Launcher "PID $($p.Id) | log: $log"
Write-Host ""
Write-Host "Field training + 20g/cycle vs same deck LucarioScorer (ladder mirror)."
Write-Host "  tail: Get-Content $log -Wait -Tail 30"
Write-Host "  stop: Stop-Process -Id $($p.Id)"

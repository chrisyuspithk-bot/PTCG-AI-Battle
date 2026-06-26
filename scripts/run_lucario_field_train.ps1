# Start Lucario field RL+MCTS (official rule opponents, Python 3.13, unbuffered log).
# Usage from repo root:
#   powershell -File scripts/run_lucario_field_train.ps1
#   powershell -File scripts/run_lucario_field_train.ps1 -Cycles 20

param(
    [int]$Cycles = 20,
    [string]$Work = 'rl_mcts_field/lucarioex_v2',
    [string]$ResumeFrom = 'rl_mcts_field/lucarioex_v1/model_best.pth'
)

$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)

$python = 'C:\Users\tobin\AppData\Local\Programs\Python\Python313\python.exe'
if (-not (Test-Path $python)) {
    Write-Error "Python 3.13 not found at $python"
}

Write-Host "Bootstrap official agents (iono/abomasnow) if needed..."
& $python scripts/bootstrap_official_rule_agents.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "bootstrap_official_rule_agents.py failed"
}

Write-Host "Verify official Kaggle rule pilots (4 archetypes, 9 field decks)..."
& $python scripts/verify_official_opponents.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "verify_official_opponents.py failed — fix pilots before training"
}

$workDir = Join-Path (Get-Location) $Work
New-Item -ItemType Directory -Force -Path $workDir | Out-Null
$log = Join-Path $workDir 'train.log'

Write-Host "Starting $Cycles cycles -> $Work (log: $log)"
Write-Host "Python: $python"

$args = @(
    '-u', 'scripts/train_lucario_field_mcts.py',
    '--device', 'cpu',
    '--cycles', "$Cycles",
    '--work', $Work,
    '--resume-from', $ResumeFrom,
    '--opponent-brain', 'native',
    '--eval-opponent', 'native',
    '--lever-blend', '0.35'
)

& $python @args 2>&1 | Tee-Object -FilePath $log
exit $LASTEXITCODE

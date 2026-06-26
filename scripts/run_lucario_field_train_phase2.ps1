# Phase-2 Lucario field RL+MCTS: resume v2 champion, **9 official field decks** per cycle.
# (Alakazam/Trevenant excluded — no Kaggle rule sample. Add --include-random-opponents to opt in.)
#
#   powershell -File scripts/run_lucario_field_train_phase2.ps1
#   powershell -File scripts/run_lucario_field_train_phase2.ps1 -Cycles 12

param(
    [int]$Cycles = 15,
    [string]$Work = 'rl_mcts_field/lucarioex_v3_phase2',
    [string]$ResumeFrom = 'rl_mcts_field/lucarioex_v2/model_best.pth',
    [double]$LeverBlend = 0.40
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

Write-Host "Phase-2 train: $Cycles cycles -> $Work"
Write-Host "Resume: $ResumeFrom | lever_blend=$LeverBlend"
Write-Host "Log: $log"

$trainArgs = @(
    '-u', 'scripts/train_lucario_field_mcts.py',
    '--device', 'cpu',
    '--cycles', "$Cycles",
    '--work', $Work,
    '--resume-from', $ResumeFrom,
    '--opponent-brain', 'native',
    '--eval-opponent', 'native',
    '--lever-blend', "$LeverBlend"
)

& $python @trainArgs 2>&1 | Tee-Object -FilePath $log
exit $LASTEXITCODE

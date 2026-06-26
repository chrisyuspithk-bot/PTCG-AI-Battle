# Fresh field-only train (no mirror) - delegates to ladder launcher.
param(
    [int]$Cycles = 25,
    [string]$Work = 'rl_mcts_field/lucarioex_v4_field',
    [double]$LeverBlend = 0.45
)

& (Join-Path $PSScriptRoot 'run_lucario_field_train_ladder.ps1') `
    -Cycles $Cycles -Work $Work -LeverBlend $LeverBlend -NoAutoResume

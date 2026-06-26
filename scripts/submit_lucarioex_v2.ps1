# Submit lucarioex_v2 field RL+MCTS champion (after daily 5/5 quota resets, UTC day).
# Package already built: dist/candidates/lucarioex_v2_field_mcts.tar.gz

$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)

$python = 'C:\Users\tobin\AppData\Local\Programs\Python\Python313\python.exe'
$archive = 'dist/candidates/lucarioex_v2_field_mcts.tar.gz'

if (-not (Test-Path $archive)) {
    & $python scripts/package_submission.py `
        --name lucarioex_v2_field_mcts `
        --scorer lucario_mcts `
        --deck agent_decks/real_mega_lucario_ex.csv `
        --model rl_mcts_field/lucarioex_v2/model_best.pth `
        --meta rl_mcts_field/lucarioex_v2/run_meta.json
}

kaggle competitions submit -c pokemon-tcg-ai-battle `
    -f $archive `
    -m "lucarioex_v2 field RL+MCTS 20-cycle vs 10 opponents"

Write-Host "Done. Track: python scripts/track_ladder.py"

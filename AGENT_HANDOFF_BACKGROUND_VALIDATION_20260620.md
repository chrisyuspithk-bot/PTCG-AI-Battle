# Agent handoff: background deep validation (2026-06-20)

Copy/paste this into the next agent.

```text
You are continuing work in `Z:\kaggle\pokemon` for Kaggle Simulation competition
`pokemon-tcg-ai-battle`.

Current goal:
Use the remaining offline time to deepen/refine the 2026-06-21 five-agent upload
slate. Public ladder mu is truth. Local gates are filters only. Do not submit to
Kaggle without explicit user approval.

Read first, in order:
1. `PROGRESS.md`
2. `TASKS.md`
3. `.cursor/SESSION.md`
4. `AGENT_HANDOFF_BACKGROUND_VALIDATION_20260620.md`
5. `data/PROJECT_PRIORITIES.md`
6. `data/SIMULATOR_RESOURCE_NOTES.md`
7. `data/COMPETITION_SCORING.md`
8. `data/SUBMISSION_PLAYBOOK.md`
9. `report/tomorrow_5_agent_slate_20260621.md`
10. `report/robust_deck_rl/deck_rl_direction_20260620.md`
11. `report/LUCARIO_V2_GATE.md`

Hard rules:
- Do not upload to Kaggle unless the user explicitly says to submit.
- Do not kill the running background jobs unless the user explicitly asks.
- Preserve dirty worktree changes you did not make.
- Simulator legal option mask is ground truth.
- Local gates are not ladder proof.
- Protected Final remains `53869254` Search Lucario at 660.5 mu until beaten.
- Daily quota for 2026-06-20 is already 5/5 used. Prepare 2026-06-21 only.

Live background state at handoff:
- PID 49372 is running:
  `C:\Users\tobin\AppData\Local\Programs\Python\Python313\python.exe scripts/robust_deck_search.py --generations 30 --population 16 --games 10 --surrogate`
- It writes:
  - `report/robust_deck_rl/metrics.csv`
  - `report/robust_deck_rl/state.json`
- Last checked state:
  - `gen_done=6/30`
  - best robust `0.4535748477470434`
  - best label `mut_x_a2_basic_heavy_31_energy_a3_starmie`
  - latest metrics row `gen=5`, robust `0.4256`, mean `0.6623`, maximin `0.3`,
    games simulated `3881`, games predicted `2143`
- PID 51432 is queued behind PID 49372:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File Z:\kaggle\pokemon\scripts\run_deep_slate_validation.ps1 -WaitForPid 49372 -RunId 20260620_141822`
- Queue log:
  `report/background_runs/deep_slate_validation_20260620_141822/run.log`
- The queued job currently waits for PID 49372, then runs:
  1. 24-game robust pool validation for:
     - `agent_decks/deck_rl/gen19_fast_basic.csv`
     - `agent_decks/top_mined_trevenant.csv`
     - `agent_decks/real_mega_lucario_ex.csv`
     - `agent_decks/a2_kyogre_33_energy.csv`
  2. 30-game public gates for:
     - `dist/candidates/track_a_lucario_search.tar.gz`
     - `dist/candidates/track_a_gen19_fast_basic_search.tar.gz`
     - `dist/candidates/track_a_trevenant_leader_search.tar.gz`
     - `dist/candidates/track_b_learned_gen19_fast_basic.tar.gz`
     - `dist/candidates/track_a_kyogre_search_backup.tar.gz`

Read-only monitoring commands:
```powershell
Get-Content Z:\kaggle\pokemon\report\robust_deck_rl\metrics.csv -Tail 10 -Wait
Get-Content Z:\kaggle\pokemon\report\robust_deck_rl\state.json
Get-Content Z:\kaggle\pokemon\report\background_runs\deep_slate_validation_20260620_141822\run.log -Tail 40 -Wait
Get-Process -Id 49372,51432 -ErrorAction SilentlyContinue
```

What to do when PID 49372 finishes:
1. Confirm PID 51432 starts writing beyond "Waiting for existing process".
2. Let PID 51432 complete unless the user asks otherwise.
3. Summarize:
   - final `report/robust_deck_rl/metrics.csv`
   - final `report/robust_deck_rl/state.json`
   - `report/background_runs/deep_slate_validation_20260620_141822/robust_pool_g24_search/summary.csv`
   - each `report/background_runs/deep_slate_validation_20260620_141822/public_gate_g30_*.txt`
4. Update `report/tomorrow_5_agent_slate_20260621.md` if the rank order changes.
5. Update `PROGRESS.md`, `.cursor/SESSION.md`, and `TASKS.md`.

Current upload slate before deeper validation:
1. `track_a_lucario_search.tar.gz` - LucarioSearch v2, best leader-suite evidence,
   first upload only after user approval.
2. `track_a_gen19_fast_basic_search.tar.gz` - robust deck Search probe.
3. `track_a_trevenant_leader_search.tar.gz` - leader-archetype Search probe.
4. `track_b_learned_gen19_fast_basic.tar.gz` - Track B probe only; learned 203/240
   vs same-deck Search 206/240, so Search remains preferred.
5. `track_a_kyogre_search_backup.tar.gz` - conservative backup/comparison.

Rejected reserve:
- `track_d_lucario_rl_mcts_iter5.tar.gz` imported and dry-run OK, but public gate
  was 8/144 = 5.6% with six 0/12 matchups. Do not upload until it beats Search
  Lucario/LucarioSearch in L1/L2.

Decision standard after background validation:
- If deeper public gates are still weak, do not upgrade any probe to Final-candidate
  language.
- If robust pool g24 changes the deck rank, update the slate but keep the ladder
  proof caveat explicit.
- Uploads on 2026-06-21 still require explicit user approval and stop/go after each
  ref reaches COMPLETE plus roughly 40 minutes of ladder games.
```

## Local files changed for this handoff

- `scripts/run_deep_slate_validation.ps1`
- `AGENT_HANDOFF_BACKGROUND_VALIDATION_20260620.md`
- `PROGRESS.md`
- `.cursor/SESSION.md`
- `TASKS.md`

## Do not treat as submitted

No Kaggle upload was performed while preparing this handoff.

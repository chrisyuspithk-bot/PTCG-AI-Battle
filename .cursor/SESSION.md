# Session state — PTCG AI Battle Challenge

> Ephemeral handoff for Cursor. **Canonical state:** `STATE.md`. **Decisions:** `RULINGS.md` (R11).

## Current focus

**20-cycle Lucario field RL+MCTS train is RUNNING** — do not kill. Official Kaggle rule
pilots per archetype (Lucario/Dragapult/Iono/Abomasnow); random for mined Alakazam/Trevenant.
Warm-started from `lucarioex_v1/model_best.pth` into `lucarioex_v2`. Cycle 0 complete
(promoted, mean eval 39.7%); cycle 1 eval in progress when handoff written. When train
finishes: validate outputs, package champion, gate vs 668 μ floor (user OK for upload).

## Key context

- **Repo:** `Z:\kaggle\pokemon` | **Branch:** `main` (1 commit ahead of origin)
- **Train log:** `rl_mcts_field/lucarioex_v2/train.log` | **metrics:** `.../metrics.csv`
- **Launch:** Python 3.13, `--cycles 20`, `--opponent-brain non_official`, `--lever-blend 0.35`
- **Opponents:** 10 field decks only (fixed `discover_opponents` — no `dragapult_ex_sample`)
- **Official agents:** `agent/official_registry.py`, `iono_agent.py`, `abomasnow_agent.py` (bootstrapped from `data/kaggle_ref/opponents/`)
- **Matchup levers:** `agent/matchup_levers.py` wired into MCTS via `set_lucario_lever_teaching`
- **Prior run:** `rl_mcts_field/lucarioex_v1/` — 5-cycle random-opponent train; `model_best.pth` = warm-start
- **Abomasnow still 0%** eval — phase-2 lever work remains after train (R11)
- **Python:** `C:\Users\tobin\AppData\Local\Programs\Python\Python313\python.exe` (not miniconda)
- **Restart script:** `scripts/run_lucario_field_train.ps1`
- **Upload:** user OK only; ≥2 stable μ readings (R1)

## Continue prompt

```text
Continue Lucario field RL train (20 cycles, official opponents). Read first: @C:\Users\tobin\.cursor\USER-RULES-PASTE-THIS.txt, @.cursor/SESSION.md, @scripts/train_lucario_field_mcts.py, @agent/official_registry.py

Goal: Let lucarioex_v2 20-cycle train finish; then validate, package, and gate champion.
Status: Train running in background; cycle 0 done (promoted); cycle 1+ in progress.
Next: Tail train.log/metrics.csv — do not kill process. When all 20 cycles complete, run validate_lucario_train_output.py and package_submission.

Branch: main | Env: Python313 | Blocker: none while train runs
```

## Timeline

- **2026-06-22T14:28Z** | 5-cycle CPU Lucario train started
- **2026-06-22T15:40Z** | handoff | conv `093ff243`
- **2026-06-22T16:30Z** | full doc sync (Session 44c)
- **2026-06-22T17:15Z** | R11 rules-before-mixture + opponent tracker | handoff by user
- **2026-06-22T15:43Z** | handoff by user | conv `093ff243` — official-opponent train v2 20 cycles started

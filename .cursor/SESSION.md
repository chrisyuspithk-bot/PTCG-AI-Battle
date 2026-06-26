# Session state — PTCG AI Battle Challenge

> Ephemeral handoff for Cursor. **Canonical state:** `STATE.md`. **Decisions:** `RULINGS.md` (R11).

## Current focus

**Best ladder pilot remains Dragapult ex** — `dragapult_ex_sample.tar.gz` (ref **53950779**, **833.0 μ** on Kaggle; peaked 850.5). Pin as a **Final Submission**; every probe must beat this bar, not merely upload.

**Lucario v5 field RL+MCTS** is training (`rl_mcts_field/lucarioex_v5_field`, PID **31692**, cycle **15+/25**). Fixed setup crash in `agent/lucario_mcts_runtime.py` (`_sample_hidden_deck_for_search`). Champion ~**43.5% field WR** (cycle 13); ladder probe **53978119** landed **600.0 μ** — far below Dragapult. Let v5 train to completion; do not swap Finals until μ **>833**.

**Next:** confirm v5 training finishes cycles 15–25; if a later `model_best` beats 43.5% field, re-package and ladder-probe; parallel path is Dragapult phase-2 levers per `ARCHITECTURE.md`.

## Key context

- **Repo:** `Z:\kaggle\pokemon` | **Branch:** `main`
- **Best pilot (ladder):** `C:\Users\tobin\Downloads\dragapult_ex_sample.tar.gz` / ref **53950779** → **833.0 μ** | `agent/dragapult_agent.py`
- **Bar to beat:** **833+ μ** (850.5 peak); mid-pack ~1100+; field top ~1350
- **Lucario v5 train:** `rl_mcts_field/lucarioex_v5_field/` — launcher `scripts/run_lucario_field_train_ladder.ps1 -Work rl_mcts_field/lucarioex_v5_field`
- **Lucario v5 submit:** ref **53978119**, `dist/candidates/lucarioex_v5_field_mcts.tar.gz`, **600.0 μ** COMPLETE
- **Lucario v2 submit:** ref **53962060**, **460.8 μ** COMPLETE
- **MCTS fix:** `agent/lucario_mcts_runtime.py` — basic-guaranteed hidden deck for `search_begin`; repro scripts in `scripts/_repro_*.py`
- **Python (GPU RL):** `C:\Users\tobin\AppData\Local\Programs\Python\Python313\python.exe`
- **Training config:** CUDA, search=20, 270 field + 20 lucario mirror/cycle, lever_blend=0.45, field gate, clock=599s
- **Specs:** `report/FIELD_TRAIN_SPEC_20260622_1730.md`, `report/LADDER_BEST_SO_FAR_20260622.md`
- **Package Lucario MCTS:** `scripts/package_submission.py --scorer lucario_mcts --model rl_mcts_field/lucarioex_v5_field/model_best.pth`
- **Standing order:** global rules → matchup levers → field mixture (R11)

## Continue prompt

```text
Continue PTCG ladder climb. Read first: @C:\Users\tobin\.cursor\USER-RULES-PASTE-THIS.txt, @.cursor/SESSION.md, @STATE.md, @RULINGS.md, @agent/lucario_mcts_runtime.py

Goal: Beat Dragapult 833+ μ (ref 53950779); keep it pinned as Final while improving.
Status: lucarioex_v5_field training cycle 15+ (PID 31692); v5 ladder probe 53978119 = 600.0 μ; MCTS setup crash fixed.
Next: Check v5 train.log for cycle 25 completion; if model_best field WR improves, re-package and ladder-probe vs 833 μ bar.

Branch: main | Env: Python313 + CUDA (not miniconda for Track B)
```

## Timeline

- **2026-06-22T15:06Z** | dragapult_ex_sample v2 submitted (fix __file__)
- **2026-06-22T21:00Z** | Dragapult **850.5 μ** — best so far (bar to beat)
- **2026-06-22T18:02Z** | lucarioex_v2 20-cycle train complete (40.5% mean eval)
- **2026-06-23T00:50Z** | lucarioex_v2 submitted ref **53962060** → **460.8 μ**
- **2026-06-23T07:36Z** | lucarioex_v5 resumed after MCTS setup crash fix (`_sample_hidden_deck_for_search`)
- **2026-06-23T11:39Z** | lucarioex_v5 submitted ref **53978119** → **600.0 μ** (probe; Dragapult still best)
- **2026-06-23T16:30Z** | handoff by user | conv `093ff243`

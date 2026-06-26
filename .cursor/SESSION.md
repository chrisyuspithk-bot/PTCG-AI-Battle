# Session state — PTCG AI Battle Challenge

> **Canonical:** `STATE.md` · **Upload gate:** `scripts/check_upload_eligible.py --suggest`

## Current focus

Session 51: **no Alakazam upload** — offline iteration only. Alakazam bench guard **default OFF** (regressed @ n=50); Dragapult levers **reverted**; latest gate **54.0%** @ n=30 vs S50 **62.0%** reference. Stable weakness vs `dragapult_ex_sample` (~33–37%). **Archaludon** ref **54083197** **COMPLETE** @ **731.3 μ** (2nd reading logged). **SearchScorer** gate fixed (battle_ptr) but **26.7%** @ n=30. **Immediate next:** replay/trace Alakazam losses vs Dragapult; `python scripts/track_ladder.py` to confirm μ stable on 54083197.

## Key context

- Repo: `Z:\kaggle\pokemon` · branch **main** (ahead 4 of origin) · Python **3.13**
- **No Alakazam upload** — user declined; need paired n=30 ≥62% before slot (R12)
- Alakazam: `agent/alakazam_agent.py` · guard OFF · `eval/alakazam_iteration_session51.md`
- Archaludon: ref **54083197** · local **72.7%** · ladder **731.3 μ** · `eval/gate_archaludon.md`
- Dragapult: **880.9 μ** hold (53989933) · full R7 guard · R12 no re-upload
- SearchScorer: **26.7%** local · bar **660.5 μ** · `eval/gate_search.md`
- Starmie ref **54083513** also submitted (PENDING) — separate row; track if needed
- Eval spine: `eval/harness.py`, `eval/gates.py`, `scripts/check_upload_eligible.py`
- Commit **3954544**: field harness + community pilots (Sessions 49–51)

## Continue prompt

```text
Continue PTCG sim — no Alakazam upload. Read first: @C:\Users\tobin\.cursor\USER-RULES-PASTE-THIS.txt, @.cursor/SESSION.md, @STATE.md, @eval/alakazam_iteration_session51.md, @RULINGS.md

Goal: Improve Alakazam offline (vs native Dragapult ~35% WR) without burning a ladder slot; monitor Archaludon ref 54083197.
Status: Bench guard OFF for Alakazam; levers reverted; Dragapult 880.9 μ hold; Archaludon 731.3 μ; user passed on Alakazam upload.
Next: Replay/trace Alakazam losses vs dragapult_ex_sample; run track_ladder.py if 54083197 needs another μ reading.

Branch: main | Env: Python 3.13 | Blocker: none — offline replay work.
```

## Timeline

- **2026-06-26T16:20:00Z** | handoff by user | conv `archaludon-ladder-probe`
- **2026-06-26T18:30:00Z** | handoff by user | conv `session51-alakazam-offline`
- **2026-06-26T22:45:00Z** | handoff by user | conv `session51-starmie-upload`
- **2026-06-26T23:00:00Z** | handoff by user | conv `session51-handoff-commit`

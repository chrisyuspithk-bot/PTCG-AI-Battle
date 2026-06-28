# Session state — PTCG AI Battle Challenge

> **Canonical:** `STATE.md` · **Upload gate:** `scripts/check_upload_eligible.py --suggest`

## Current focus

**Session 57 — R11 ladder probe in flight.** R10 (854 μ) and R8a (967 μ) ruled out; champion **54083197 @ 1196.1 μ** retained. Implemented **R11** `_prize_race_attach_cap` on R7 baseline (R8a reverted); local gate **58.7%** n=150; probe **54138853** uploaded 2026-06-28T11:42 UTC — **PENDING**. **Next:** wait ≥40 min → `track_ladder.py`; when COMPLETE pull episodes + decide vs 1196.1 μ. R12 dead-active retreat (82062971) only if R11 misses.

## Key context

- **Repo:** `Z:\kaggle\pokemon` · **Branch:** main · **Env:** Python 3.13
- **Champion (R12 — do not re-upload):** ref **54083197** @ **1196.1 μ** · `agent_decks/archaludon_ex_cinderace.csv`
- **Probe PENDING:** **54138853** (R7+R11 attach cap) · local **58.7%** · see `eval/ladder_log.csv`
- **Ruled out:** R10 854 · R8a 967 · R8a+R8b 984 · R9 841
- **R11 code:** `agent/archaludon_agent.py` — `_prize_race_attach_cap` in `apply_overrides`
- **R11 logic:** behind + legal lethal attack on Active → cap attach/tempo ≤5000, boost KO ≥55000; skip if empty bench needs basic
- **Champion losses (50 ep):** prize 10 · no_active 4 · deck_out 1 · WR 70.0%
- **Prize-loss DS:** 10/10 behind race; 24 attach-over-attack when lethal legal; close losses 82062971, 82073113, 82073596
- **Deck logs:** `report/deck_logs/archaludon/` · iteration: `eval/archaludon_iteration.md`
- **Episode pull blocker:** Kaggle 429 on replays — retry `analyze_submission.py --ref <ref> --skip-fetch`
- **Replace champion only if** probe beats **1196.1 μ** on ≥2 readings ≥40 min apart
- **Queued if R11 fails:** R12 dead-active retreat (Relicanth stall, 82062971)

## Continue prompt

```text
Continue Archaludon R11 ladder probe. Read first: @C:\Users\tobin\.cursor\USER-RULES-PASTE-THIS.txt, @.cursor/SESSION.md, @STATE.md, @eval/ladder_log.csv, @eval/archaludon_iteration.md

Goal: Read μ for probe 54138853 (R11); pull episodes if COMPLETE; decide vs champion 54083197 @ 1196.1 μ.
Status: R11 uploaded 2026-06-28T11:42 UTC, PENDING; R10/R8a ruled out; R8a reverted from agent.
Next: python scripts/track_ladder.py (≥40 min since upload); analyze_submission + extract_deck_perspective_logs per ref when COMPLETE.

Branch: main | Env: Python 3.13 | Do not re-upload 54083197 (R12).
```

## Timeline

- **2026-06-28T12:00:00Z** | handoff by user | conv `handoff-s57`
- **2026-06-28T11:42:29Z** | R11 probe **54138853** uploaded
- **2026-06-28T11:28:38Z** | R10/R8a probes COMPLETE (ruled out)
- **2026-06-27T00:00:00Z** | handoff by user | conv `35cee825`

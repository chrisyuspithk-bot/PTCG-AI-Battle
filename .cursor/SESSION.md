# Session state — PTCG AI Battle Challenge

> **Scoreboard:** `report/LADDER_BEST_SO_FAR.md`

## Current focus

Archaludon ladder iteration: **R12 dead-active tempo** probe **54139502** uploaded and **PENDING** (local gate **70.7%** n=150). Leader unchanged **54083197 @ 1196.1 μ** (Ruling R12 — do not re-upload that ref). **Next:** wait ≥40 min → `python scripts/track_ladder.py` for **54139502**; log μ in `eval/ladder_log.csv` + `report/LADDER_BEST_SO_FAR.md`.

## Key context

- **Repo:** `Z:\kaggle\pokemon` · **Branch:** `main` (ahead of origin; not pushed)
- **Python:** ≥3.11 on user machine (3.13 for gate/package)
- **Leader:** ref **54083197** @ **1196.1 μ** — R7 bench guard only on ladder
- **In flight:** ref **54139502** — R7 + R12 `_dead_active_tempo_score` (uploaded 2026-06-28T12:13 UTC)
- **R11 probe:** ref **54138853** @ **632.9 μ** (reading 2; local 58.7%) — logged, not leader
- **R12 lever:** dead Active (Relicanth ≤25% HP or ≤25% + 0 energy) → boost bench attach/retreat, penalize END when metal in hand
- **Trace:** close loss **82062971** (Relicanth stall vs energizing bench Duraludon)
- **Agent:** `agent/archaludon_agent.py` · **Gate:** `python scripts/gate_archaludon.py --games 30 --suite full --report`
- **Track:** `python scripts/track_ladder.py` · **Analyze:** `python scripts/analyze_submission.py --ref <ref> --skip-fetch`
- **Posture:** log every probe; low μ = learning data, not permanent ban; ship **new catalog rows** only
- **Blocker:** Kaggle API **429** on replay download for some probes — retry analyze when rate limit clears
- **Last commit:** `046b430` (R11 + S55–57); this session adds R12 code + tracking (commit pending handoff)

## Continue prompt

```text
Continue Archaludon R12 ladder track. Read first: @C:\Users\tobin\.cursor\USER-RULES-PASTE-THIS.txt, @.cursor/SESSION.md, @report/LADDER_BEST_SO_FAR.md, @agent/archaludon_agent.py

Goal: fetch ladder μ for probe 54139502 and log vs leader 1196.1.
Status: R12 PENDING (local 70.7%); leader 54083197 @ 1196.1 μ; R11 54138853 @ 632.9 μ.
Next: python scripts/track_ladder.py (≥40 min since upload) → update eval/ladder_log.csv + LADDER_BEST_SO_FAR.md.

Branch: main | Do not re-upload 54083197 (R12).
```

## Timeline

- **2026-06-28T12:13** | R12 probe **54139502** uploaded (local 70.7%)
- **2026-06-28** | R11 **54138853** → **632.9 μ** (reading 2)
- **2026-06-28T12:30:00Z** | handoff by user | conv `d4865d78`

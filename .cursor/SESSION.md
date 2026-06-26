# Session state — PTCG AI Battle Challenge

> **Canonical:** `STATE.md` · **Upload gate:** `scripts/check_upload_eligible.py --suggest`

## Current focus

Session 51 closed with **Starmie ladder upload** (ref **54083513**, PENDING) — new `starmie_rules` × ashleysandlin deck, PrizeTracker, finish search, R7 bench guard; local mirror **56.7%** n=30 (full field **9.3%**). **Archaludon** ref **54083197** COMPLETE @ **731.3 μ** (2nd reading). **Alakazam** held offline (**54–62%** local; bench guard OFF, levers reverted — no upload). **SearchScorer** harness fixed (`battle_ptr` refresh) but **26.7%** @ n=30 vs **660.5 μ** bar. **Immediate next:** `python scripts/track_ladder.py` after Starmie COMPLETE; ≥2 μ readings ≥40 min for 54083513 and 54083197.

## Key context

- Repo: `Z:\kaggle\pokemon` · branch **main** (ahead of origin) · Python **3.13**
- **Starmie upload:** ref **54083513** PENDING · package `dist/candidates/starmie_froslass_ashleysandlin.tar.gz` · `scripts/package_starmie.py`
- **Archaludon:** ref **54083197** · local **72.7%** · ladder **731.3 μ** (2nd reading)
- **Dragapult hold:** **880.9 μ** (53989933) · R12 no re-upload without material change
- **Alakazam:** guard default OFF · `eval/alakazam_iteration_session51.md` · no upload until ≥62% ×2
- **SearchScorer:** `agent/search_policy.py` + `PrizeTracker` · **26.7%** · bar **660.5 μ**
- **Eval spine:** `eval/harness.py`, `eval/gates.py`, `field/registry.json`, `scripts/gate_*.py`, `scripts/check_upload_eligible.py`
- **Community pilots:** `agent/alakazam_agent.py`, `agent/archaludon_agent.py`, `agent/starmie_agent.py`
- **Starmie field:** `agent/prize_tracker.py`, `agent/finish_search.py`, suite `starmie` in registry
- **R7 shared:** `agent/empty_bench_guard.py` · Dragapult full guard · Alakazam guard OFF
- **Catalog:** `eval/AGENT_CATALOG_FULL.md` · ladder log `report/ladder_history.csv`

## Continue prompt

```text
Continue PTCG sim Session 52. Read first: @C:\Users\tobin\.cursor\USER-RULES-PASTE-THIS.txt, @.cursor/SESSION.md, @STATE.md, @eval/AGENT_CATALOG_FULL.md, @RULINGS.md

Goal: Track new ladder rows (Starmie 54083513, Archaludon 54083197); iterate SearchScorer or Alakazam offline without duplicate uploads.
Status: Starmie submitted PENDING; Archaludon 731.3 μ; Alakazam upload declined; SearchScorer 26.7% local.
Next: python scripts/track_ladder.py after Starmie COMPLETE; wait ≥40 min for stable μ on both refs.

Branch: main | Env: Python 3.13 | Blocker: ladder PENDING on 54083513.
```

## Timeline

- **2026-06-26T16:20:00Z** | handoff by user | conv `archaludon-ladder-probe`
- **2026-06-26T18:30:00Z** | handoff by user | conv `session51-alakazam-offline`
- **2026-06-26T22:45:00Z** | handoff by user | conv `session51-starmie-upload`

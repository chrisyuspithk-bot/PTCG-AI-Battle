# eval/ — measurement & session artifacts

**Ground truth:** Kaggle public μ → [`AGENT_CATALOG_FULL.md`](AGENT_CATALOG_FULL.md) · [`ladder_log.csv`](ladder_log.csv) · [`ladder_scoreboard_full_20260626.md`](ladder_scoreboard_full_20260626.md)

**Spine (local filter only):** `eval/harness.py`, `eval/gates.py`, `field/registry.json`, `field/weights.json`

## Read before train/upload

[`AGENT_CATALOG_FULL.md`](AGENT_CATALOG_FULL.md) — all 21 submissions: brain type, deck, training opponents, verdict.

## Harness API

```powershell
# SearchScorer — home-grown 660.5 mu bar (Lucario deck)
python scripts/gate_search.py --games 30 --suite full --report

# LucarioScorer rules only (39.3% @ n=30 — do not upload)
python scripts/gate_lucario_rules.py --games 30 --suite full --report

# Dragapult ladder ship track (880.9 mu)
python scripts/package_dragapult.py
python scripts/gate_dragapult.py --games 30 --suite full --report

# Pilot×deck (never swap brain onto wrong list)
python scripts/gate_dragapult.py --games 30 --suite full --hero-deck agent_decks/real_mega_lucario_ex.csv

# Meta + smoke
python scripts/analyze_meta_by_mu_band.py --download-per-band 50
python -m pytest tests/test_harness_smoke.py -q
```

## Session artifacts

| Session | File | Content |
|---------|------|---------|
| **49** | `AGENT_CATALOG_FULL.md` | Every agent decoded |
| **49** | `pilot_deck_matrix_session49.md` | dragapult brain 10% on Lucario deck |
| **49** | `ladder_log.csv` | 21 rows synced from Kaggle |
| **48** | `dragapult_baseline_session48.md` | Boss levers ruled out |
| **46** | `lucario_rules_baseline_session46.md` | LucarioScorer 44% @ n=20 local |

Resubmit: `data/SUBMISSION_REGISTRY.md` · Protocol: `data/EVAL_PROTOCOL.md`

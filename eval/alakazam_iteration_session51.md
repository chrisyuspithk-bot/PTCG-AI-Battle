# Alakazam iteration — Session 51

**Date:** 2026-06-26  
**Pilot:** `agent/alakazam_agent.py` × `ryotasueyoshi_alakazam_best5.csv`  
**Ladder bar:** 659.0 μ (53913404) — **do not re-upload without sustained local uplift**

---

## Bench guard A/B (@ n=50, full suite)

| Variant | Overall WR | no_active |
|---------|------------|-----------|
| No guard | 56.8% | 1 |
| + guard (tempo-safe MAIN) | 53.6% | 1 |

**Decision:** Alakazam **bench guard default OFF** (`ALAKAZAM_BENCH_GUARD=0`). Guard regressed WR without fixing no_active. Dragapult keeps full guard (880.9 μ ladder).

See `eval/alakazam_bench_guard_ab.md`.

---

## Dragapult matchup levers (reverted)

Tried Boss +6000 vs Dragapult line, early Battle Cage boost, Enhanced Hammer bump → **58.7%** @ n=30 (below 62% S50 baseline). Reverted to notebook scores.

---

## Gate snapshots (same deck, n=30 — high variance)

| Run | Overall WR | vs dragapult_ex_sample |
|-----|------------|------------------------|
| S50 baseline (no guard) | **62.0%** | 36.7% |
| + bench guard | 57.3% | 43.3% |
| + dragapult levers | 58.7% | 36.7% |
| Revert levers (this run) | 54.0% | 33.3% |

**Interpretation:** n=30 full suite swings ~8 pp run-to-run. **Do not upload** on a single reading below 62%. Need n≥50 paired runs or two n=30 readings before spending a slot.

---

## Dragapult pilot (unchanged stack)

Official Crispin rules → **full R7 bench guard** → never-crash. Hold **880.9 μ** (53989933). R12 blocks re-upload.

A/B @ n=50: guard +6.7 pp at n=30 earlier; n=50 mixed (55.2% vs 56.8% off) — variance.

---

## Infrastructure shipped

- `agent/empty_bench_guard.py` (shared; `respect_main_tempo` flag)
- `scripts/compare_alakazam_bench_guard.py`
- `scripts/compare_dragapult_bench_guard.py`
- Package bundles `empty_bench_guard.py`
- `make_alakazam_brain(bench_guard=False)` default

---

## Next

1. **Replay pull** on Alakazam losses vs `dragapult_ex_sample` (why 33–37% stable weakness).
2. **Paired gate:** two n=30 runs; upload only if both ≥62% and beat 53913404 hypothesis documented.
3. **Optional:** `top_mined_alakazam.csv` only if second deck beats notebook on dragapult @ n=50 without losing Lucario.

**Commands:**
```powershell
python scripts/compare_alakazam_bench_guard.py --games 50 --suite full --report
python scripts/gate_alakazam.py --games 30 --suite full --report
python scripts/check_upload_eligible.py --suggest
```

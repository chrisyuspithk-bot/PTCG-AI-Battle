# Kaggle Status — Session 45 (2026-06-26)

**Synced via:** `track_ladder.py`, `kaggle competitions submissions -v`, `analyze_submission.py`

---

## Active submissions (COMPLETE)

| Ref | File | μ | Submitted | Agent | Notes |
|-----|------|--:|-----------|-------|-------|
| **53989933** | `dragapult_ex_sample.tar.gz` | **880.8** | 2026-06-23 | dragapult v3 (R7 bench guard) | **Best pilot.** Beats v2 (850.5) and v2 recent (833.0). **Pin as Final.** |
| **53995982** | `lucarioex_v5_field_mcts.tar.gz` | **580.6** | 2026-06-24 | lucario_mcts v5 final | Pre-R2 levers in tarball. Converged from 600.0 → 580.6. |
| 53950779 | `dragapult_ex_sample.tar.gz` | 833.0 | 2026-06-22 | dragapult v2 | Superseded by v3 — unpin if still Final |
| 53978119 | `lucarioex_v5_field_mcts.tar.gz` | 464.7 | 2026-06-23 | lucario_mcts cycle13 probe | Superseded by 53995982 |

## Convergence

| Ref | μ history (recent) | Stable? |
|-----|-------------------|---------|
| 53989933 | 684.9 → **880.8** | Yes (COMPLETE, settled) |
| 53995982 | 600.0 → **580.6** | Yes (COMPLETE, settled) |

## Episode analysis (partial — Kaggle API 429 on bulk log fetch)

| Ref | Episodes parsed | W/L/D | Win rate | Avg turns | Fast loss % | Top loss |
|-----|-----------------|-------|----------|-----------|-------------|----------|
| 53995982 | 0 (replay parse incomplete) | — | — | — | — | — |
| 53989933 | 3 | 2/1/0 | 66.7% | 13.7 | 100% | prize |

Dragapult v3: small sample; fast games typical for Dragapult pilot. No `no_active` losses observed in prior sessions.

## Decision gate

| Check | Result |
|-------|--------|
| Lucario μ ≥ 573.8 | **580.6 ≥ 573.8** → **FULL SPEED** |
| Lucario μ < 550 | No — proceed |
| Dragapult bar | 880.8 > 850.5 → v3 is new floor |
| R2 package on ladder | **No** — `lucarioex_v5_r2_levers_20260626.tar.gz` not uploaded |
| R2 upload timing | **Defer** until after Abomasnow local gate |

## User actions (web UI)

1. **Pin Dragapult v3 (53989933 @ 880.8 μ)** as Final Submission
2. Unpin Dragapult v2 (53950779) if still active
3. Keep Lucario v5 (53995982) as second Final until post-Abomasnow package uploads

## Session 45 proceed

**Decision: PROCEED** to Abomasnow R2 lever iteration (local sandbox).

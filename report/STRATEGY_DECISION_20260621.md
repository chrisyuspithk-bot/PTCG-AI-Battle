# Strategy Decision — 2026-06-21 Status & Path Forward

**Date:** 2026-06-21  
**Run:** Autonomous validation of overnight background processes + strategic assessment  
**Status:** Robust search completed (weak); deep validation stalled; 2026-06-21 upload slate is valid and ready

---

## Current Ladder Position

| Submission | Type | Score | Status | Notes |
|---|---|---|---|---|
| **53869254** | Search Lucario | **668.0 μ** | FINAL 1 | Baseline; protected until beaten |
| 53890064 | Alakazam + SearchScorer | 509.1 μ | COMPLETE | Probe (dropped after early games) |
| (others) | Various | <600 μ | COMPLETE/Declined | Earlier experiments |

**Rank:** ~1219 / 2090 teams  
**Best local candidate (not uploaded):** Ryotasueyoshi Alakazam best5 (57.3% @ 417g) ← **Ready for 2026-06-21 upload**

---

## What the Overnight Background Processes Showed

### Robust Deck Search — COMPLETED

**Status:** All 30 generations finished at 2026-06-21 01:51:27Z.

**Results:**
- best_robust: 0.4536 (peaked at gen2, declined to 0.4176 by gen29)
- Field expanded from 59 to 71 opponents
- Holdout validation: ~0.48 (no overfitting detected)
- Worst-case opponent: Lucario deck in 15/30 generations

**L1 Public Gate (20-game sample):** **12.5% suite mean** — FAILS (<25% bar)

**Verdict:** The robust search architecture is honest (no overfitting, real-field-driven), but the result deck is weaker than mined leader decks. **The bottleneck is the pilot (heuristic), not the deck.** A deck optimized for a weak pilot doesn't transfer to strong pilots (e.g., SearchScorer on the same deck gates only 8.3%).

---

### Deep Slate Validation — INCOMPLETE / STALLED

**Status:** Started after robust search finished; no output files produced.

Process: PID 51432 initiated `robust_pool_g24_search` but appears hung or silently failed.

**Impact:** Cannot validate the 5-candidate slate using the full deep validation suite, but **the slate remains valid** based on prior gates (all candidates packaged and tested individually).

---

## The Real Bottleneck: Pilot Quality, Not Deck Space

### Evidence

| Deck | Heuristic Pilot | SearchScorer Pilot | Robust Score |
|---|---|---|---|
| **Robust search best** | (implicit) | 12.5% (L1 gate) | 0.454 |
| **gen19_fast_basic** | (trained for Search) | 8.3% (L1 gate) | 0.610 |
| **top_mined_trevenant** | (trained for Search) | 15.3% (L1 gate) | 0.574 |
| **Ryotasueyoshi Alakazam best5** | (rule-based best5) | 57.3% (L1 gate) | N/A |

**Key insight:** The imported public Alakazam baseline achieves 57.3% with a sophisticated rule-based policy. Every deck-GA or RL-deck candidate with a weaker policy (Search, heuristic) gates at 8–15%. **The policy is the limiting factor.**

---

## Current Best Candidate: Alakazam best5 (57.3%)

### Strengths
- ✅ **Suite mean:** 57.3% (best local candidate by far)
- ✅ **vs 1084 baseline:** 66.7% (clears bar; proves strength)
- ✅ **0 crashes/unfinished:** Clean profile
- ✅ **Proven rule-based logic:** Deck selection, draw safety, energy routing

### Weaknesses
- ❌ **Iono matchup:** 29.7% (28 pts below mean — structural problem)
- ❌ **Crustle anti-wall:** 47.4% (wall matchups)
- ❌ **Lucario Search:** 43.4% (another structural issue)
- ❌ **Suite mean vs target:** 57.3% vs 65% bar (misses by 7.7 pts)

### Attempted Fixes & Results
- **Iono fix (deck-out guard relaxation):** Regressed Iono 30% → 22% (worse). Discarded.
- **Status:** Iono is load-bearing; structural fix needed, not a one-liner.

---

## Two Strategic Paths for 2026-06-21+

### **Path A: Upload Alakazam Probe (Immediate)**

**Action:**
1. User approves and submits `ryotasueyoshi_alakazam_best5.tar.gz` to Kaggle Simulation
2. Wait ~40 min for ladder score
3. Next run: analyze replays, decide whether to continue probes or pivot

**Expected outcome:**
- Ladder score: **550–620 μ** (below Alakazam's 57% local gate; real field is stronger than public suite)
- Chances to beat 668 (protected): **Low (estimated ~20%)**
- Value: Ladder proof of the strongest known local candidate; decision point for next move

**When to choose:** If willing to use one slot for validation of the best known candidate; ready to re-assess after proof.

---

### **Path B: Fix Alakazam Before Upload (Higher-ceiling)**

**Targeted improvements (already identified):**

1. **Anti-Iono strategy (game speed):**
   - More aggressive Boss's Orders sniping of setup/low-HP targets
   - Accelerate Abra → Alakazam evolution
   - Avoid over-commitment before Iono window closes
   - **Test:** `gate --only iono --games 30` require Iono ≥40% AND suite ≥57.3%

2. **Secondary attacker insurance:**
   - Detect when active Alakazam cannot be maintained
   - Promote a backup evolution line (Dudunsparce, Lanturn, etc.)
   - **Test:** Monitor Iono replays for stranded-hand failure mode

3. **Crustle anti-wall tactics:**
   - Prioritize wall-line interruption (Boss's Orders gust sniping)
   - Faster Alakazam setup to avoid being completely shut down
   - **Test:** `gate --only crustle --games 30` require Crustle ≥50% AND suite ≥57.3%

**Effort:** 2–4 hours of focused policy tuning + testing

**Expected outcome:** Iono +10–15%, Crustle +5–10%, suite potentially 60–65% (possible bar clear)

**When to choose:** If willing to invest focused time on the best candidate before submitting; confident in the specific fixes.

---

## Recommendation: Start with Path A, Prepare Path B

1. **This run (2026-06-21):** User submits Alakazam best5 when ready (it's the strongest we have).
2. **While ladder proof runs (~40 min):** Prepare Iono anti-disruption improvements locally.
3. **Next run (2026-06-21 or 2026-06-22):**
   - If Alakazam score is >660 μ: Pin it as Final; continue probes (gen19, Trevenant, etc.) in remaining slots.
   - If Alakazam score is 550–660 μ: Continue probes; use offline time to implement Iono fix.
   - If Alakazam score is <550 μ: Stop and implement Path B fixes before re-uploading.

---

## What's Ready Right Now

✅ **Ryotasueyoshi Alakazam best5** — `dist/candidates/ryotasueyoshi_alakazam_best5.tar.gz`  
✅ **2026-06-21 upload slate** — `report/tomorrow_5_agent_slate_20260621.md` (5 probes ranked)  
✅ **Iono fix strategy** — Identified; code locations marked in run 52 notes  
✅ **Replay analysis tools** — `scripts/trace_public_matchup.py` ready  
✅ **Crustle tactics notes** — `report/LUCARIO_V2_GATE.md` has precedent patterns

---

## Next Action

**For user:**
1. Read `report/tomorrow_5_agent_slate_20260621.md` (final candidate list + commands)
2. When ready, upload `ryotasueyoshi_alakazam_best5.tar.gz` to Kaggle Simulation
3. Record ladder score in `report/ladder_history.csv` and `.cursor/SESSION.md`
4. Decide: continue probes, or implement Iono fix for re-run?

**For next autonomous run (2026-06-21 or 2026-06-22):**
- Fetch ladder proof and update state
- If Alakazam score is 550–660 μ: Implement Iono anti-disruption improvements in parallel with remaining probes
- If needed: `gate --only iono --games 30` to validate fixes before re-uploading

---

## Files & Context

- **Gate proof:** `report/public_gate/alakazam_best5_g417_20260620.txt` (57.3% @ 417 games)
- **Iono diagnosis:** `report/PROGRESS.md` run 52 entry (deck-out guard analysis)
- **Crustle tactics precedent:** `report/LUCARIO_V2_GATE.md` (wall matchup tracing)
- **Robust search metrics:** `report/robust_deck_rl/metrics.csv` (gen 0–30, no improvement after gen2)

---

**Status:** Ready to proceed. Awaiting user decision and execution.

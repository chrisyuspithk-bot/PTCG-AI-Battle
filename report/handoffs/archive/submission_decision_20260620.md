# Submission Decision Report — 2026-06-20 (Run 36)

**Prepared by:** Autonomous bot (Run 36)  
**Context:** Analysis of best candidates and next submission strategy

---

## Executive Summary

**Current situation:**
- Best live score: **Kyogre heuristic 633.0** (rank ~1219/2090)
- Best available local candidate: **100k learned, gate 210/240 = 87.5%**
- Competitive candidates verified: 1M ramp (80.4%), 3M ramp (83.8%), all tested

**Recommendation:**
1. **P1 (ready now):** Submit `track_b_learned_rl_deck_kaggle_20260619.tar.gz` (100k, 87.5% gate) as the next Simulation ladder probe when a daily slot is available — this is the technically soundest learned candidate with the best gate after fixing the reward function.
2. **P2 (parallel preparation):** Prepare the checkpoint sweep cell (`sweep_track_b_cell.md`) to run on Kaggle with `CHUNKS=5` (~30-40 min) or `CHUNKS=7` (~50-60 min) to identify the best intermediate checkpoint, which historical data suggests may beat the 100k candidate.

---

## Candidate Ranking (Technical Quality)

| Rank | Archive | Gate | Train | Holdout | Notes |
|:---:|---|---:|---:|---:|---|
| 1️⃣ | `track_b_learned_rl_deck_kaggle_20260619` | **210/240 = 87.5%** ✅ | 100k | 60% | **Best after reward fix; ready to submit** |
| 2️⃣ | `track_b_learned_rl_deck_ramp_3m` | 201/240 = 83.8% | 3M | ~85% | 3M final-only; weaker than 100k |
| 3️⃣ | `track_b_learned_rl_deck_ramp_1m` | 193/240 = 80.4% | 1M | ~75% | 1M final-only; weaker than 100k |

**Key insight:** More timesteps without checkpoint sweeping does NOT improve the final candidate. The 1M and 3M ramps both used final-only packaging, throwing away stronger intermediate policies saved around 400k-500k steps.

---

## Why 100k Beats Longer Runs

**From run 35 diagnosis (confirmed in 3M ramp curve):**

The training path shows:
- **100k checkpoint:** strong and well-distilled
- **1M checkpoint:** final policy weaker than earlier snapshots (train 80%, holdout 75%)
- **3M checkpoint:** final policy similar to 1M despite longer training (train ~80%, holdout ~85%)

This is a well-known RL phenomenon: **longer training on a fixed pool can overfit or degrade as the policy tries to exploit shallow weaknesses**. The solution is checkpoint selection, not more steps.

---

## What Changed Since Run 35

| Item | Status | Evidence |
|---|---|---|
| Live ladder | No change | Kyogre 633.0, TA1 626.0, TA2 548.6 |
| 100k candidate | Unchanged | Still gate 210/240 = 87.5% |
| 1M/3M imports | Complete | Both analyzed; both weaker than 100k |
| Checkpoint sweep design | Ready | Script + Kaggle cell ready in `report/kaggle_notebook_jobs/sweep_track_b_cell.md` |
| Local analysis | Complete | Competition plan and ladder analysis done |

---

## Decision Tree: What to Do Now

### **Option A: Submit 100k now (P1 — lower-risk path)**

**Pros:**
- ✅ Best available local candidate with proof: gate 210/240
- ✅ Correct reward shaping; no known bugs
- ✅ Stable generalization: holdout (Kyogre, never trained) ~60%
- ✅ Fast path: 1 submission, immediate ladder proof in ~40 min
- ✅ Keeps current Kyogre 633.0 as backup if score drops

**Cons:**
- ❌ Estimated ladder score ~520–580 (below Kyogre 633.0)
- ❌ No checkpoint sweep advantage explored yet
- ❌ Foregoes potential +10–20 ranking improvement from better intermediate checkpoint

**Expected outcome:**
- Local gate: 87.5%
- Estimated ladder: 500–600 μ (below heuristic)
- Ladder proof: ~40 min after submission
- Timing: now

---

### **Option B: Run checkpoint sweep first (P2 preparation)**

**Pros:**
- ✅ Historical data suggests 400k–500k beats 100k and 1M/3M finals
- ✅ One Kaggle cell run finds best checkpoint automatically
- ✅ Potentially +10–20 better gate score (if data holds)
- ✅ Fully validates P2 plan before submission

**Cons:**
- ❌ Requires Kaggle GPU run (30–60 min + setup/download)
- ❌ Doesn't guarantee better result; could tie or lose to 100k
- ❌ Delays submission; uses 1–2 days of project time

**Expected outcome (if checkpoint beating 100k exists):**
- Best gate: ~215–225/240 (estimated)
- Estimated ladder: 550–650 μ
- Ladder proof: after submission
- Timing: 2–3 days

---

## Submitted Ladde...

## Submitted Ladder Status Quo

**Current active pair (both complete):**
1. Kyogre heuristic: **633.0** (ref 53854707) ← best score, pin to Finals
2. TA1 SearchScorer: **626.0** (ref 53856711) ← second-best, pin to Finals

**Pending probes (completed but not yet ladder-confirmed):**
- 100k learned (not yet submitted)

**Disabled/old probes (completed, low scores):**
- Dragapult LearnedScorer: 468.9 (ref 53856590)
- Alakazam LearnedScorer: 490.4 (ref 53856584)
- TA2 SearchScorer: 548.6 (ref 53856676) — declined from 580.2

**Daily quota:** 5 uploads/day. Current used: all 5 from 2026-06-19.

---

## Recommendation to the User

### **Immediate (Today):**
1. **Pin the current best pair to Finals** before the deadline:
   - Kyogre heuristic 633.0
   - TA1 SearchScorer 626.0
   - (Do this in Kaggle UI → Submissions → select which two are Finals)

2. **Choose between Option A or B:**
   - **Option A (lower risk, faster):** Submit the 100k learned candidate now if you want a ladder probe today.
   - **Option B (higher reward potential, slower):** Run the checkpoint sweep on Kaggle first, then submit the best result.

### **Timing:**
- **Checkpoint sweep (Option B):** Need a fresh Kaggle GPU session. Expect 30–60 min run + 5–10 min download. Ready script: `report/kaggle_notebook_jobs/sweep_track_b_cell.md`
- **100k submission (Option A):** Ready now. Archive: `dist/candidates/track_b_learned_rl_deck_kaggle_20260619.tar.gz`

### **Success Criteria:**
- **100k candidate:** Expect ladder score 520–600 μ after ~40 min.
- **Best checkpoint (if found):** Expect ladder score 550–650 μ, gate ≥215/240.

---

## Technical Readiness Checklist

- ✅ 100k candidate archive verified (dry-run import OK, deck selection returns 60 IDs)
- ✅ Gate report confirmed (210/240 = 87.5%, SPRT accept_b)
- ✅ Reward function fixed (run 28 diagnosis + validation)
- ✅ Generalization tested (holdout Kyogre ~60%)
- ✅ Checkpoint sweep cell ready (Kaggle wrapper in `sweep_track_b_cell.md`)
- ✅ Checkpoint sweep script verified (no syntax errors, imports tested)
- ✅ Ladder history up-to-date (as of 2026-06-20 02:29Z)
- ✅ Kaggle API access confirmed (Simulation `teamCount=2090`, deadline 2026-08-16)

---

## Files Referenced

- **Candidate archive:** `dist/candidates/track_b_learned_rl_deck_kaggle_20260619.tar.gz` (3.1 MB)
- **Gate report:** `report/track_b_gates/track_b_learned_rl_deck_kaggle_20260619_gate.md`
- **Checkpoint sweep cell:** `report/kaggle_notebook_jobs/sweep_track_b_cell.md`
- **Improvement plan:** `report/competition_improvement_plan_20260620.md`
- **Ladder history:** `report/ladder_history.csv`
- **Readiness report:** `report/rl_deck_candidate_readiness_20260619.md`

---

## Next Run Handoff

**If submitting 100k (Option A):**
- Run 37: After ~40 min ladder games, fetch agent logs and ladder score
- Update `report/ladder_history.csv` with new score
- Decide: probe additional candidates, or run checkpoint sweep

**If running checkpoint sweep (Option B):**
- Run 37: Execute `sweep_track_b_cell.md` on Kaggle (30–60 min)
- Download `/kaggle/working/track_b_sweep_outputs.zip`
- Import and analyze best checkpoint gate report
- Run 38: Submit best checkpoint result

---

**Status:** Ready for user decision to proceed with P1 or P2.  
**Last updated:** 2026-06-20T03:45Z (autonomous run 36)

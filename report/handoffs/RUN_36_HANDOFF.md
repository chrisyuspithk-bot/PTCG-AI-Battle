# Run 36 Handoff — Ready for User Decision

**Date:** 2026-06-20  
**Status:** All analysis complete. Awaiting user decision on P1 vs P2.  
**Runbook:** See `report/submission_decision_20260620.md` (full decision analysis)

---

## Current State

**Live ladder (as of 2026-06-20 02:29Z):**
- Kyogre heuristic: **633.0** (best score, ref 53854707)
- TA1 SearchScorer: **626.0** (second-best, ref 53856711)
- TA2 SearchScorer: 548.6 (declined from 580.2)

**Best available local candidates:**
1. **100k learned (210/240 = 87.5%)** ← Ready now
2. 3M ramp learned (201/240 = 83.8%)
3. 1M ramp learned (193/240 = 80.4%)

**Key insight:** Longer training without checkpoint sweeping does NOT improve gate scores. The 1M and 3M runs used final-only packaging, throwing away stronger intermediate checkpoints.

---

## Two Options Available

### **Option A: Submit 100k Learned Now (P1 — immediate path)**

**Archive:** `dist/candidates/track_b_learned_rl_deck_kaggle_20260619.tar.gz` (3.1 MB)

**What happens:**
1. User submits archive to Kaggle Simulation (uses 1 of 5 daily slots)
2. Agent starts ladder games (~40 min to completion)
3. Final score appears in leaderboard
4. Expected score: 520–600 μ (below Kyogre 633.0)

**Why this option:**
- ✅ Fastest ladder proof (immediate)
- ✅ Best known local candidate (gate 210/240)
- ✅ Keeps Kyogre 633.0 as backup
- ✅ Clear data point for next decision

**When to choose:** If you want immediate ladder validation and are comfortable with estimated score 520–600.

---

### **Option B: Run Checkpoint Sweep First (P2 — higher-ceiling path)**

**Execution:** Follow `report/checkpoint_sweep_execution_guide.md`

**What happens:**
1. User opens Kaggle Notebook, enables GPU, runs cell from `report/kaggle_notebook_jobs/sweep_track_b_cell.md`
2. Script trains 5 or 7 chunks of 100k timesteps each (30–60 min GPU time)
3. Saves and gates each checkpoint
4. Re-distills best two finalists with more teacher episodes (800 vs 300)
5. Packages and gates best result
6. User downloads `/kaggle/working/track_b_sweep_outputs.zip`
7. Next run: analyze best checkpoint gate, compare to 100k baseline
8. If better: submit best checkpoint; if not: submit 100k

**Expected outcome:**
- Best checkpoint likely: 400k–500k steps
- Estimated gate: 215–225/240 (vs 100k at 210/240)
- Estimated ladder: 550–650 μ (vs 100k at ~520–600)

**Why this option:**
- ✅ Addresses root cause of 1M/3M failure (final-only packaging)
- ✅ Potential +10–20 ladder score improvement
- ✅ Fully validates P2 plan before submission
- ❌ Takes 2–3 days total (Kaggle run + analysis + submission)

**When to choose:** If you want the strongest possible learned candidate and have time for a GPU run.

---

## What's Ready Right Now

| Item | Status | Location |
|---|---|---|
| Best learned candidate archive | ✅ Ready | `dist/candidates/track_b_learned_rl_deck_kaggle_20260619.tar.gz` |
| Gate report (100k) | ✅ Verified | `report/track_b_gates/track_b_learned_rl_deck_kaggle_20260619_gate.md` |
| Readiness analysis | ✅ Complete | `report/rl_deck_candidate_readiness_20260619.md` |
| Decision matrix | ✅ Complete | `report/submission_decision_20260620.md` |
| Checkpoint sweep cell | ✅ Ready | `report/kaggle_notebook_jobs/sweep_track_b_cell.md` |
| Checkpoint sweep script | ✅ Verified | `scripts/sweep_track_b_checkpoints.py` |
| Execution guide (P2) | ✅ Ready | `report/checkpoint_sweep_execution_guide.md` |
| Ladder history | ✅ Current | `report/ladder_history.csv` (as of 2026-06-20 02:29Z) |

---

## Action Items for User

### **Immediate (1 minute):**

**Pin current best pair to Finals** in Kaggle UI:
1. Go to Kaggle → Competitions → pokemon-tcg-ai-battle-challenge-strategy → Submissions
2. Scroll to your submissions list
3. Find refs `53854707` (Kyogre 633.0) and `53856711` (TA1 SearchScorer 626.0)
4. Click "Select" for each to pin as Final 1 and Final 2
5. (This ensures if you submit new probes, the best score stays in the active pair)

### **Then, choose one:**

**Option A (fast, now):**
- Submit `dist/candidates/track_b_learned_rl_deck_kaggle_20260619.tar.gz` to Kaggle Simulation
- Expect ladder proof in ~40 min
- Next run: fetch logs, decide next move

**Option B (strong, 2–3 days):**
- Open a Kaggle Notebook, enable GPU
- Copy cell from `report/kaggle_notebook_jobs/sweep_track_b_cell.md`
- Run the cell (30–60 min)
- Download output zip when done
- Next run 37: extract, analyze, compare to 100k baseline
- Run 38 or later: submit best result

---

## Key Files for Each Path

**If choosing Option A (submit 100k):**
- Archive: `dist/candidates/track_b_learned_rl_deck_kaggle_20260619.tar.gz`
- Gate proof: `report/track_b_gates/track_b_learned_rl_deck_kaggle_20260619_gate.md`
- Command: Upload to Kaggle Simulation, record submission ID

**If choosing Option B (checkpoint sweep):**
- Cell to run: `report/kaggle_notebook_jobs/sweep_track_b_cell.md`
- Execution guide: `report/checkpoint_sweep_execution_guide.md`
- Script being called: `scripts/sweep_track_b_checkpoints.py`
- Comparison baseline: 100k gate (210/240)

---

## Timeline Estimates

| Path | Total Time | Ladder Proof | Next Submission |
|---|---|---|---|
| **A (submit 100k now)** | ~1 hour | ~40 min after submit | Anytime after proof |
| **B (checkpoint sweep)** | 2–3 days | After sweep done + analysis | 2–3 days from now |

---

## Context for Next Run

**If run 37 is submitted-after-A:**
- New submission ID appears on ladder immediately
- Fetch logs with `python scripts/track_ladder.py --fetch-logs`
- Update `report/ladder_history.csv` with new score
- Decide: submit additional probes, or prepare next candidate?

**If run 37 is after-B (checkpoint sweep):**
- Download `/kaggle/working/track_b_sweep_outputs.zip` from Kaggle
- Extract to `report/kaggle_notebook_jobs/sweep_outputs_<date>/`
- Analyze `best_gate.json` and `checkpoint_*_gate.md` files
- Compare best checkpoint gate to 100k baseline (210/240)
- Prepare best result for submission in run 38

---

## Analysis Documents

All detailed analysis is ready in these files:

1. **`report/submission_decision_20260620.md`** — Full decision matrix, why 100k beats 1M/3M, pros/cons of A vs B
2. **`report/checkpoint_sweep_execution_guide.md`** — Step-by-step execution, troubleshooting, expected outputs
3. **`report/competition_improvement_plan_20260620.md`** — Diagnosis of checkpoint-sweep issue, P0–P5 priorities
4. **`report/rl_deck_candidate_readiness_20260619.md`** — 100k candidate validation, training proof, generalization test
5. **`report/ladder_analysis_20260619.md`** — Interpretation of current ladder scores and field gaps

---

## No Blockers

✅ All technical work complete  
✅ Candidates verified and ready  
✅ Checkpoint sweep cell ready  
✅ Analysis complete  
✅ Awaiting user decision (A or B) and execution

**Status: Ready to proceed.**


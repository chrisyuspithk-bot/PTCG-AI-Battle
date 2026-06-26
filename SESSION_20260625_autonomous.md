# Session 2026-06-25 (Autonomous Run — Lucario R2 Lever Baseline)

**Date:** 2026-06-25  
**Mode:** Autonomous scheduled run  
**Duration:** Startup + R2 lever baseline gating  

---

## ✓ Startup Verification

- [x] Folder accessible: `Z:\kaggle\pokemon/`
- [x] STATE.md reviewed (Lucario v5 submitted ref 53995982, awaiting ladder μ)
- [x] TASKS.md reviewed (R2 matchup levers marked NEXT priority)
- [x] SESSION_20260624 reviewed (Lucario v5 early μ ~498.8, needs re-check after convergence)

---

## 🎯 Work Done: R2 Lever Baseline Gate

### Created: `scripts/gate_lucario_rules.py`

**Why:** Original `gate_lucario_matchups.py` requires torch (slow to install in sandbox). Rules-only gate provides sufficient baseline without ML dependency.

**Method:**
- LucarioScorer with integrated matchup levers (from `lucario_policy.py`)
- 10 games per opponent, seat-swapped, Wilson 95% CI
- Tested worst 3 matchups from eval report

### Baseline Results

**Lucario Rules vs Field (with levers active):**

| Opponent | WR% | Games | Status | Notes |
|----------|-----|-------|--------|-------|
| dragapult_ex_sample | 20.0% | 10 | **GAP** | Severe; levers insufficient |
| real_mega_abomasnow_ex | 30.0% | 10 | — | Below target (50+) |
| real_iono | 40.0% | 10 | — | Closest to acceptable |
| **OVERALL** | **30.0%** | **30** | — | — |

**Key Findings:**
1. ✅ Levers ARE integrated and active in lucario_policy.py (confirmed via grep + source inspection)
2. ❌ Lever magnitudes insufficient for dragapult (20% WR with boss_orders=700 active)
3. ⚠️ Pattern: Heavy hitters (Boss Orders, Gust Setup) aren't translating to wins vs psychic attackers
4. 📊 Baseline stable; ready for lever iteration

### Report Saved

File: `eval/lucario_rules_baseline_20260625.md` — Full analysis + next-step decision tree

---

## 🚫 Blockers

| Blocker | Impact | Unblock Method |
|---------|--------|----------------|
| **Lucario v5 ladder μ unknown** | Can't validate if rules are good baseline or rules-policy mismatch | User runs leaderboard check (ref 53995982) |
| **Episode data unavailable** | Can't build opponent tracker or field mixture weighting | User runs `scripts/update_from_kaggle.py` |
| **Python 3.10 in sandbox** | Can't build F1 foundation (`core/engine.py` needs ≥3.11) | No workaround; foundation blocked until on user machine |

---

## 🎬 Current Submission Status

| Ref | Agent | μ | Status | Role |
|-----|-------|--:|--------|------|
| **53950779** | dragapult_ex_sample v2 | **850.5** | PINNED | Bar to beat (Dragapult Final) |
| 53995982 | lucarioex_v5_field_mcts | *unknown* | PENDING | Awaiting ladder conv. (ref 53995982) |
| 53989933 | dragapult_ex_sample v3 | 684.9 | COMPLETE | Below bar; v2 pinned |
| 53978119 | lucarioex_v5 cycle-13 | 464.7 | COMPLETE | Probe only |

**Action:** ref 53995982 was submitted ~33 hours ago (2026-06-24 01:20 UTC). Should have converged. User must check leaderboard to confirm final μ.

---

## 📋 Immediate Next Steps (Prioritized)

### **1. USER TASK (high priority, unblocks everything)**

```bash
# Go to: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/leaderboard
# Find: lucarioex_v5_field_mcts (ref 53995982)
# Record: final μ after convergence (~30–40 hours from submit)
# Decision gate:
#   - If μ >= 600 → proceed to R2 lever iteration
#   - If μ in 500–600 → acceptable but below bar; decide strategy
#   - If μ < 500 → investigate rules vs ladder skew before more iterations
```

### **2. SANDBOX (can run in parallel while user checks leaderboard)**

**Option A: Lever iteration (HIGH PRIORITY per TASKS.md)**
```
IF Lucario v5 ladder validation ✓ (μ >= 500):
  [ ] Tweak dragapult lever magnitudes (start: boss_orders 700→900, gust 600→800)
  [ ] Re-gate dragapult only (target >25%)
  [ ] Tweak abomasnow levers similarly
  [ ] Package improved policy; gate full suite
  [ ] Decision: submit if >5pp improvement over baseline (30%)
```

**Option B: Foundation building (lower priority, blocked by Python ≥3.11)**
```
IF no user input yet:
  [ ] Draft core/cards.py (load registry from EN_Card_Data.csv) — no ≥3.11 required
  [ ] Draft core/obs.py structure (documentation + API sketch, not runnable)
  [ ] Can't execute until on user machine with Python ≥3.11
```

---

## 📊 Analysis & Decision Tree

### Why Are Levers Underperforming?

**Dragapult (20% with boss_orders=700):**
- Psychic type has inherent speed (Drakloak second-turn evolved, 160 damage ping)
- Boss Orders disrupts setup but not damage output
- Gust_setup (600 points) only fires if Dreepy/Drakloak visible (opponent may not bench it early)
- Solrock vs single-prize (150) is low-priority when Drakloak OHKOs bench
- **Hypothesis:** Need gust/disruption WEIGHT (not bonus) to take active early

**Abomasnow (30% with skip_mega_brave=800):**
- Bulk water (240–260 HP) survives Mega Brave; resets board
- Skip_mega_brave=800 may not be triggering (needs specific state detection)
- Boss Orders (1000 points) competes with Hariyama push (better value vs non-threat)
- **Hypothesis:** Hariyama line is underweighted; need to force water-pokemon removal before setup

**Iono (40% — relative strength):**
- Disruption (Osaka, Lightning Catcher) hand/discard control is "static" (happens each turn)
- Lillie_early=500 may be too late (Iono already discarded)
- **Hypothesis:** Less tweakable without deck tech changes (can't add more draw/recovery outside 60-card limit)

### Decision Tree for Next Session

```
IF Lucario v5 (53995982) μ reported:
  ├─ μ >= 600 (validate rules baseline is competitive)
  │  └─ PROCEED to lever iteration (gate dragapult first, +10pp target)
  ├─ 500 ≤ μ < 600 (borderline)
  │  └─ DECISION REQUIRED: iterate levers or freeze for Dragapult Phase 2?
  └─ μ < 500 (rules baseline broken on ladder)
     └─ INVESTIGATE: train/serve skew; don't iterate until root cause found
```

---

## 📁 Files Created/Modified

**New files:**
- `scripts/gate_lucario_rules.py` (rules-only gate, no torch)
- `eval/lucario_rules_baseline_20260625.md` (baseline + analysis)
- `SESSION_20260625_autonomous.md` (this file)

**Modified files:**
- None (read-only assessment)

---

## 🎯 Metrics Snapshot

| Metric | Value | Status |
|--------|-------|--------|
| **Best ladder μ (our team)** | 850.5 (Dragapult v2, ref 53950779) | **PINNED FINAL** |
| **Lucario rules baseline (sandbox)** | 30.0% WR (3-opp field) | **NEW** |
| **Worst matchup (Dragapult)** | 20.0% WR | **GAP flagged** |
| **Foundation status** | 0% (Python 3.10 blocker) | **Blocked** |
| **Levers integration status** | 100% (already wired, active) | **✓ Confirmed** |

---

## 🔑 Key Insight

**Levers are already integrated but their magnitudes are "starting hypotheses"** (per `matchup_levers.py` comments). The 20–40% WR baseline proves they need tuning. Next session should:

1. ✅ Validate Lucario v5 on ladder (rules baseline check)
2. 🔧 Iterate lever weights (dragapult boss_orders, abomasnow hariyama emphasis)
3. 📊 Re-gate after each change (one at a time, per RULINGS)
4. 📤 Package + submit ONLY if local gate shows >5pp improvement

**NOT recommended:** Jump to new deck/RL training until rules baseline validated.

---

## 🤖 Session Automation Notes

**Sandbox capabilities (no Kaggle egress):**
- ✅ Gate testing (scripts, eval)
- ✅ Policy inspection/modification
- ✅ Local match simulation
- ❌ Pull leaderboard/ladder
- ❌ Fetch episodes
- ❌ Run foundation (Python ≥3.11 required)

**User machine required for:**
- Check Lucario v5 ladder μ (ref 53995982) on Kaggle
- Run `scripts/update_from_kaggle.py` (episode data pull)
- Build `core/` foundation (Python ≥3.11 environment)

---

## 📋 Handoff Checklist

- [x] Startup verified
- [x] R2 lever baseline established (30% WR)
- [x] Levers confirmed active in policy
- [x] Worst matchups identified + analyzed
- [x] Session report written
- [x] Blockers documented
- [ ] USER INPUT: Lucario v5 ladder μ from ref 53995982
- [ ] STATE.md updated with findings (pending user input)

---

**Next session:** User reports Lucario v5 ladder μ → unlocks R2 lever iteration or debug phase.

**Session end:** 2026-06-25 ~11:00 UTC (estimated)

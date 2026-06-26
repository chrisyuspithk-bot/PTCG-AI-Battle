# Action Plan — Session 2026-06-25 Results

## Critical Discovery: Dragapult v3 Improved to 858.7!

**Ladder update (user-reported):**
- Lucario v5 (ref 53995982): **573.8 μ** ✓ Validated
- **Dragapult v3 (ref 53989933): 858.7 μ** ← **BEATS v2 (850.5)**

---

## Immediate Action (Kaggle, ~5 min)

### ⚡ **1. Unpin Dragapult v2; Re-pin Dragapult v3**

**Current:** v2 (850.5) is pinned as Final Submission  
**Problem:** v3 (858.7) is now higher; v2 should not be holding the slot  
**Action:**  
1. On Kaggle, go to your Submissions page
2. **Unpin** dragapult_ex_sample v2 (ref 53950779)
3. **Pin** dragapult_ex_sample v3 (ref 53989933) as your Final Submission
4. Confirm: v3 badge appears on leaderboard

**Why:** v3 holds a stronger floor (858.7 vs 850.5); better defensive position.

---

## Conditional Action (Sandbox, ~2–4 hours if starting now)

### ✅ **2. R2 Lever Iteration (Unlocked — Rules Baseline Validated)**

**Condition:** Lucario v5 @ 573.8 > 500 threshold → ✓ PASS  
**Status:** Proceed to lever tuning

**High-Priority Target:** Dragapult matchup (20% WR locally → target >25%)

**Steps:**
```
1. Edit: agent/matchup_levers.py
   - Dragapult line: boss_orders 700 → 900
   - Dragapult line: gust_setup_pokemon 600 → 800

2. Gate: python scripts/gate_lucario_rules.py --opponents dragapult_ex_sample --games 20
   - Target: >25% WR (currently 20%)
   - If yes → commit change
   - If no → revert; try next lever combo

3. Repeat for abomasnow (30% → target >40%)
   - Lever: hariyama_vs_ex (currently 300) → try 500–800
   - Lever: skip_mega_brave_vs_bulk_single_prize (currently 800) → try 1200

4. Full re-gate (all 3 worst opponents)
   - Target: >35% overall (currently 30%)
   - If yes → package policy v2; gate vs Dragapult best (858.7)
   - If yes + >5pp local improvement → submit as Slot 2
```

**Gate script ready:** `scripts/gate_lucario_rules.py` (created this session)

---

## Decision Tree by Timeline

### If you have **5–10 minutes:**
→ **Just do the Kaggle action (unpin v2, re-pin v3).** That's the critical move.

### If you have **2–4 hours:**
→ **Kaggle action + R2 lever iteration (1–2 lever tweaks, quick re-gate).**

### If you have **4+ hours:**
→ **Full R2 phase:** dragapult + abomasnow levers, full re-gate, validation, package.

---

## Success Metrics

**Kaggle action:** ✓ Once v3 is pinned, you're defending at 858.7 μ (vs 850.5 before).

**Lever iteration:** 
- Local gate improvement: >5pp (30% → 35%+)
- Ladder validation: Lucario v6 > 573.8 μ (need at least 600+ to be competitive with Dragapult)

---

## Files Reference

**For lever iteration:**
- `agent/matchup_levers.py` — Edit lever magnitudes here
- `scripts/gate_lucario_rules.py` — Run this to test changes
- `eval/lucario_rules_baseline_20260625.md` — Baseline report (hypothesis notes)

**For submission:**
- `dist/` — Package output goes here (if ready to submit)
- `report/` — Any eval reports from re-gates

---

## Unblocked / Blocked Status

**✅ UNBLOCKED (can proceed):**
- R2 lever iteration (Lucario v5 validation passed)
- Dragapult v3 re-pinning (immediate, high confidence)

**⚠️ BLOCKED (needs more from you):**
- Episode data pull (user machine: `scripts/update_from_kaggle.py`)
- Field mixture (R3) weighting (depends on episode data)
- Foundation (F1–F3) — needs Python ≥3.11 on user machine

---

## Next Autonomous Session

Will pick up from:
1. Dragapult v3 re-pinning status (confirmed on Kaggle?)
2. Any R2 lever iteration progress (local gate results)
3. Decide: submit new Lucario v6 if >5pp improvement, or hold for more work

Bring: Screenshot of re-pinned v3, local gate results (if any).

---

**This plan unlocks immediate progress with minimal risk.**

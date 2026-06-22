# Alakazam Anti-Iono Improvement Plan

**Date:** 2026-06-22 (Session 43b — Autonomous continuation)  
**Target:** Improve Iono matchup from 13.3% → 40%+ (gate target)  
**Status:** ⏸️ Awaiting focused code modifications

---

## Current State

**Baseline (ryotasueyoshi_alakazam_best5):**
- Iono WR: **13.3%** (4-26 on 30-game sample)
- Historical: **29.7%** (per AGENT_DEEP_DIVE_20260622.md, n=417)
- Variance likely (small sample size on 30 games)

**Gate Command:**
```bash
python scripts/gate_vs_public.py \
  --agent dist/candidates/ryotasueyoshi_alakazam_best5.tar.gz \
  --only iono --games 30
```

---

## Path to 40%+ Iono WR

Per STRATEGY_DECISION_20260621.md §Path B:

### Fix 1: Faster Alakazam Evolution

**Current problem:** Agent waits for optimal conditions; against Iono, speed is critical.

**Solution:** Prioritize Rare Candy + Alakazam evolution earlier in game.

**Code location:** `main.py` → `estimate_hand_increase()` and evolution priority scoring
- Increase priority weight for "evolve Alakazam" action when turn count is low (turn < 4)
- Prioritize Rare Candy plays more aggressively
- Get Alakazam active by turn 2-3 (vs current turn 3-4)

**Implementation effort:** Low (parameter tweaks)

---

### Fix 2: Earlier Boss's Orders Sniping

**Current problem:** Agent plays Boss's Orders reactively; Iono decks prey on setup Pokémon.

**Solution:** Play Boss's Orders turn 1-2 vs disruptors (vs turn 3-4 normally).

**Code location:** `main.py` → Boss's Orders priority section
- Detect opponent disruptor patterns (many discards, Poffin plays, etc.)
- Boost Boss's Orders priority when disruptor detected
- Snipe low-HP setup targets (Duskull, Slowpoke, etc.) earlier

**Implementation effort:** Medium (needs disruptor detection logic)

---

### Fix 3: Hand Size Management

**Current problem:** Large hand pre-Iono = huge damage swing. Alakazam relies on hand size for damage, but gets punished.

**Solution:** Better hand management against disruptors.

**Code location:** `main.py` → draw strategy and hand optimization
- Avoid holding >7 cards vs likely Iono decks
- Play cards from hand more aggressively (don't stack unnecessarily)
- Consider discarding less-critical cards proactively before opponent's Iono turn

**Implementation effort:** Medium (requires game state tracking)

---

## Why My First Attempt Failed

Attempted Python code modifications introduced a scoping issue:
```python
if op_has_iono_threat:  # Variable defined inside conditional, used outside scope
    evolution_priority_boost = 1.5
```

**Lesson:** Modifying rule-based agents requires careful scope and control flow handling.

---

## Safer Approach: Smaller, Testable Changes

Instead of all-at-once modifications, implement in order:

1. **Change 1: Tweak evolution timing**
   - Modify: priority weights for Rare Candy + evolution actions
   - Test: Gate on Iono (quick validation)
   - Proceed if improved or stable

2. **Change 2: Boss's Orders priority**
   - Build on Change 1
   - Add disruptor detection
   - Test: Gate on Iono
   - Proceed if improved

3. **Change 3: Hand management**
   - Build on Changes 1-2
   - Add hand-size constraints
   - Final validation: Full suite gate (Iono + all others)

---

## Success Criteria

**L1 (Iono-only) gate:**
- Iono WR ≥ 40% (minimum 12/30 wins on 30-game sample)
- No crashes/unfinished games

**L2 (Full suite) gate:**
- Suite mean ≥ 57.3% (no regression from baseline)
- Iono ≥ 40%
- Other matchups stable or improved

---

## Next Steps (For Next Session)

1. **Extract and analyze** the current Alakazam agent code in detail
2. **Implement Change 1** (evolution timing tweaks) with careful testing
3. **Gate immediately** after each small change
4. **Iterate** until either 40% Iono or clear blockers found

**Alternative:** If code modification proves too risky, explore:
- Using a pre-built competitive Alakazam variant (if available)
- Delegating to a search-based scorer instead of rule-based tweaks
- Accepting baseline and moving to next candidate (Trevenant)

---

## Grounding

- **Target:** AGENT_DEEP_DIVE_20260622.md §P3 (Alakazam Iono hole)
- **Strategy:** STRATEGY_DECISION_20260621.md §Path B (Anti-Iono fixes)
- **Current baseline:** Gate run 2026-06-22 13:3% (iono vs baseline)
- **Historical comparison:** 29.7% from AGENT_DEEP_DIVE (417-game sample, may be different Iono opponent)

---

**Status:** 🔴 **BLOCKED ON CODE MODIFICATIONS** — Need careful implementation to avoid breaking working agent

**Recommendation:** Proceed with methodical, tested approach (Change 1 → gate → Change 2 → gate → Change 3 → gate)

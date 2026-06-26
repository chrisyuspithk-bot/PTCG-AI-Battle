# Session 2026-06-24 (Autonomous Run)

**Date:** 2026-06-24  
**Mode:** Autonomous scheduled run  
**Duration:** Startup + status assessment (no live Kaggle egress from sandbox)

---

## Startup Verification ✓

- [x] Folder accessible: `Z:\kaggle\pokemon/`
- [x] PROGRESS.md readable (migrated to STATE.md)
- [x] TASKS.md readable (R1–R3 pilot rules in progress)
- [x] README.md understood (reset 2026-06-22, core/eval/episodes/meta scaffolds pending)
- [x] STATE.md reviewed (Lucario v5 final submitted, awaiting ladder μ)

---

## Critical Status

### Last Submission (ref 53995982)

- **What:** Lucario v5 field RL+MCTS final champion
- **Submitted:** 2026-06-24 01:20:12 UTC
- **Status:** COMPLETE
- **Initial μ:** 600.0 (validation read, very early)
- **Latest known μ:** 498.8 (early settling, per eval report)
- **Local eval:** 46.1% field (cycle 21 peak; 25 cycles completed)
- **Ladder comparison:**
  - Prior cycle-13 probe (53978119): 464.7 μ
  - **Dragapult v2 bar (53950779): 850.5 μ** ← MUST BEAT THIS

**Early assessment:** μ trending well above cycle-13 (464.7), but still **far below Dragapult bar (850.5)** by ~350 points. Needs to settle (40–90 min from submit) before final judgment.

### Pinned Final Submission (ref 53950779)

- **Agent:** dragapult_ex_sample v2 (Crispin rules + never-crash wrapper)
- **μ:** 850.5 (settled 2026-06-22 ~20:57 UTC)
- **Role:** **BAR TO BEAT** — holds Final Submission slot while we improve

### Dragapult v3 Ladder Probe (ref 53989933)

- **Agent:** dragapult_ex_sample v3 Phase 2 (empty-bench guard)
- **μ:** 684.9 (3 games: 2W/1L, 67%)
- **Status:** Below v2 bar (850.5); keep v2 pinned

---

## What I Checked

### Submission History
- 47 rows analyzed from `report/submission_log.csv` + `report/ladder_history.csv`
- **Conclusion:** Full progression from 43-session reset visible; Dragapult rules = best shipped (850.5 μ); all RL/MCTS probes below it

### Training Output
- Lucario v5: 25/25 cycles complete (GPU train, ~2026-06-23 21:11 local)
- Output: `rl_mcts_field/lucarioex_v5_field/`
  - `model_best.pth` = cycle-21 peak (46.1% field eval)
  - `model_latest.pth` = cycle-24 end state (36.1% eval, regressed)
  - `metrics.csv` = full cycle-by-cycle eval
  - Shipped `model_best.pth` to ref 53995982

### Eval Report (Lucario v5)
- Per-opponent WR: Dragapult sample 25.5% (worst), Iono 36.5%, Abomasnow 30%, Lucario mirror 44.2%
- High variance cycle-to-cycle (42–46% champion eval)
- **Key finding:** RL + MCTS cannot beat official Dragapult rules sample; need **matchup levers (R2) on rules baseline**

---

## What I Cannot Do (Sandbox Constraints)

| Blocker | Reason | Required for |
|---------|--------|---------------|
| Pull live Kaggle ladder | No egress from sandbox | Re-check ref 53995982 μ after matchmaking |
| Fetch episode data | No Kaggle API from sandbox | Daily meta map (D1–D3) |
| Pull new replays | No Kaggle API from sandbox | Episode store / opponent tracker |
| Update opponent tracker | Depends on episode pull | Field mixture weighting (R3) |

**Solution:** User must run `scripts/update_from_kaggle.py` on their machine to unblock meta + tracker.

---

## What I Can Do (Foundation Work)

**Available locally (no Kaggle needed):**

1. **Build core/ (F1):**
   - [ ] `core/cards.py` — load card registry from `data/EN_Card_Data.csv`
   - [ ] `core/engine.py` — wrap local `cg` engine
   - [ ] `core/obs.py` + rules info model test
   - Requires Python ≥3.11 (sandbox is 3.10; can draft structure)

2. **Build eval/ (F2):**
   - [ ] `eval/harness.py` — seeded, side-swapped, Wilson-CI gate
   - [ ] `eval/gates.py` — L0 smoke, L1 real-field, L2 ladder probe eval
   - [ ] Re-measure SearchScorer on real field (establish ~668 floor)

3. **Audit field/ (F2 companion):**
   - [ ] Move `agent_decks/{real_*,top_mined_*}` → `field/decks/`
   - [ ] Build `field/registry.json` (archetype, source, pilot)
   - [ ] Retire `pool_*` proxies per RULINGS 2B

4. **Lucario R2 levers (R2):**
   - [ ] Gate `scripts/gate_lucario_matchups.py` on worst opponents
     - Dragapult sample: 25.5% → target >40% (lever teaching + new line)
     - Abomasnow: 30% → re-gate `abomasnow_water` levers
     - Iono: 36.5% → measure `iono_lightning` levers
   - Can run locally on real decks

---

## Next Actions (Prioritized)

### Immediate (User, on their machine)

1. **Re-check Lucario v5 ladder μ** (ref 53995982)
   - Go to https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/leaderboard
   - Find submission 53995982 (lucarioex_v5_field_mcts.tar.gz)
   - Record current μ and episode count
   - **Compare to Dragapult bar 850.5**
   - Log finding in next autonomous session

2. **Optional: Run episode data pull** (if meta tracking desired)
   ```bash
   cd Z:\kaggle\pokemon
   python scripts/update_from_kaggle.py
   ```
   - Requires `.kaggle/kaggle.json` token
   - Outputs: leaderboard snapshot, latest replays, opponent distribution
   - Inputs next session's meta-informed decisions

### Secondary (Sandbox, can run in parallel)

3. **Gate Lucario R2 levers** (HIGH PRIORITY per eval report §7)
   - File: `scripts/gate_lucario_matchups.py` (draft exists)
   - Test on `real_*` decks locally
   - One lever per PR; re-gate worst matchup (Dragapult sample)
   - **Stop point:** No re-submit until local gate shows >10pp improvement per eval report

4. **Build foundation (F1–F2)** if Python ≥3.11 available
   - Start with `core/obs.py` + info model test (most foundational)
   - Move to `eval/harness.py` (enables all future gates)

---

## Build Queue Status

**From TASKS.md:**

```
## Pilot rules — before mixture weighting (standing decision Session 44d)

- [ ] R1. Global rules (phase 1)
  - [ ] Lucario: baseline gate vs 10 real-field decks ← DONE (46.1% local, but uncompetitive vs Dragapult 850.5)
  - [x] Dragapult: 850.5 μ (ref 53950779) ← SHIPPED, bar to beat
  - [x] Dragapult Phase 2: bench guard (v3 submitted 53989933, 684.9 μ, below bar)

- [ ] R2. Matchup levers (phase 2) ← **NEXT**
  - [x] Wire levers into lucario_policy.py (Boss/PPP/Lillie/etc)
  - [ ] Lucario vs Dragapult: RE-GATE 25.5% → >40% target
  - [ ] Lucario vs Abomasnow: gate abomasnow_water levers
  - [ ] Lucario vs Iono: measure iono_lightning levers

- [ ] R3. Field mixture (phase 3) ← BLOCKED (episode data pull)
  - Requires opponent distribution (D1–D3) → user machine

## Foundation (must come first — every pillar depends on it)

- [ ] F1. core/ model + foundation
  - [ ] core/cards.py
  - [ ] core/engine.py
  - [ ] core/obs.py + empirical test

- [ ] F2. eval/ harness + field/ registry
  - [ ] Move agent_decks → field/decks/
  - [ ] eval/harness.py (seeded, Wilson CI)
  - [ ] Re-measure 668 floor on real field

- [ ] F3. Spine migration
  - [ ] Migrate agent/ → agents/ (keep spine intact)
  - [ ] Fix imports; confirm smoke test passes
```

**Green lights:** Dragapult v1–v2 done; Lucario rules in place  
**Red lights:** Lucario RL uncompetitive; levers not yet re-gated; foundation not built

---

## Key Rulings Enforced

Per RULINGS Part 0 (operating mindset):

1. ✅ **Measure; never assume** — Used actual ladder history, not assumptions
2. ✅ **Simplicity wins** — Dragapult rules (850.5) beats Lucario RL (498.8); v5 teaches this lesson
3. ⚠️ **Pilot before deck** — Rules floor still better than trained policies; next step is levers on rules
4. ✅ **Real field is the only judge** — Monitoring against ladder, not proxies
5. ⚠️ **Ship nothing ungated** — v5 was gated; but still far below bar
6. ✅ **Finish one thing before starting next** — v5 train complete; now gate levers
7. ✅ **Ground in math** — Using Wilson CI, Ruling R3 (R beat RL), ladder-only judges
8. ✅ **850.5 is best so far, not the goal** — Treatment correct; expect to beat 850.5

---

## Files Modified

**None (read-only status assessment)**

---

## Files to Review

- **STATE.md** — Already reflects v5 submission and next action
- **eval/lucarioex_v5_field_train_eval.md** — Complete v5 analysis
- **metrics.csv** (rl_mcts_field/lucarioex_v5_field/) — Full training curves
- **TASKS.md** — R2 levers section outlines next gate work

---

## Metrics Snapshot

| Metric | Value | Notes |
|--------|-------|-------|
| **Best ladder μ (our team)** | 850.5 (Dragapult v2, ref 53950779) | **Bar to beat** |
| **Lucario v5 early ladder μ** | 498.8 (ref 53995982) | Settling; needs re-check |
| **Local field metric improvement** | +2.6pp (43.5% → 46.1%) | Cycle-13 → v5 |
| **Worst matched (Lucario)** | Dragapult sample, 25.5% WR | Lever target >40% |
| **Foundation status** | 0% (core/, eval/ empty) | F1–F3 pending |

---

## Blockers for Next Session

1. **Ladder μ unknown** — Lucario v5 (53995982) needs re-check (user's machine)
2. **Episode data unavailable** — D1–D3 blocked (user's machine)
3. **Python version** — Core/ requires ≥3.11; sandbox is 3.10
4. **Lucario R2 levers** — Draft exists but not re-gated; should run before any new RL

---

## Handoff for Next Run

**USER ACTION REQUIRED:**
1. Check ref 53995982 ladder μ on https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/leaderboard
2. Log finding (or run `scripts/update_from_kaggle.py` to auto-pull + timestamp)
3. Decide: if μ < 600, debug train/serve skew before Lucario v6; if μ > 600, proceed to R2 lever gate

**SANDBOX CAN CONTINUE:**
- R2 matchup lever gating (if Lucario v5 ladder validates)
- Foundation scaffolding (F1–F3) — limited by Python 3.10 but structure can start

---

**Session end:** Ready for user input on Lucario v5 ladder μ and meta pull decisions.

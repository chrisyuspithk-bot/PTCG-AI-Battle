# Updated Instructions — Post-Alakazam Submission (2026-06-21)

**Status:** Alakazam best5 submitted 1 hour ago; monitoring ladder performance  
**Submission slots:** 4 remaining today (5/day limit per `OFFICIAL_COMPETITION_RULES_SIMULATION_20260621.md`)  
**Finals slots:** 2 available (per rules)  
**Deadline:** August 16, 2026 (per `OFFICIAL_OVERVIEW_SIMULATION_20260621.md`)

---

## 🎯 Today's Mission

**Goal:** Validate Alakazam ladder performance + decide on remaining 4 submissions

---

## 📊 PHASE 1: MONITOR ALAKAZAM (Next 30–60 min)

### What to Track

1. **Current μ (Skill Rating)** — Refresh leaderboard → find Alakazam entry
2. **σ² (Uncertainty)** — Should decrease as more episodes run
3. **Win/loss pattern** — Note which decks beat it, which it beats
4. **Early matchups vs Iono** — The known weakness (Iono gates 29.7% from earlier testing)

### Where to Look

- Kaggle Leaderboard: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/leaderboard
- Search: Your submission by name or timestamp
- Track: μ, σ², episode count, recent results

### Decision Trigger

**If μ < 500 after 20+ episodes:**
- Alakazam underperforming vs expected 550–620 range
- Possible: Weaker opponents in current pool, or regression from gate testing
- Action: Prepare alternative (Trevenant or Kyogre) for slot 2

**If 500 ≤ μ ≤ 620:**
- On track per `report/STRATEGY_DECISION_20260621.md` forecast
- Action: Decide on remaining 3 slots (test new decks or hold)

**If μ > 620:**
- Exceeding forecast; strong validation
- Action: Consider uploading improvements or reserving Finals slots

---

## 🎯 PHASE 2: DECISION TREE FOR REMAINING SLOTS (2–5)

### Decision Point A: Test New Decks vs Hold Reserve?

**Option A1: Test Alternatives (Slot 2)**
- Upload Trevenant (`15.3%` gate, `0.556` robust gauntlet)
- Rationale: Validate different archetype; compare vs Alakazam directly
- Risk: Uses 1 slot on lower-performing deck
- Timeline: 20 min upload + monitoring

**Option A2: Test Improved Alakazam Variant (Slot 2)**
- Minor tweak to Alakazam (e.g., Iono counter-tech from `report/STRATEGY_DECISION_20260621.md`)
- Rationale: Iterative improvement on proven baseline
- Risk: Marginal gains; won't fix structural Iono weakness
- Timeline: 20 min deck edit + upload

**Option A3: Hold Reserve (Keep 3 slots in reserve)**
- Wait 4–8 hours for Alakazam μ to stabilize
- Rationale: More data = better decision on what to test
- Benefit: Can pivot if Alakazam underperforms
- Timeline: Monitor passively, decide evening

---

### Decision Point B: Finals Slot Strategy

**Per `OFFICIAL_OVERVIEW_SIMULATION_20260621.md`:**
- You can select up to 2 Final Submissions
- Evaluated Aug 17–31 (final convergence period)

**Options:**
1. **Commit Alakazam as Final 1 now** — Lock in best-known deck
2. **Hold Finals decisions until Aug 15** — See how ladder settles
3. **Designate slot 2 as potential Final** — If it outperforms Alakazam

**Recommendation:** Don't lock Finals until Aug 10 (let ladder data mature)

---

## 🛠️ PHASE 3: EXECUTION TEMPLATE

### If Choosing A1 (Test Trevenant)

```
Slot 2 — Trevenant (SearchScorer pilot)
- Deck: agent_decks/top_mined_trevenant.csv
- Brain: SearchScorer (reference)
- Expected gate: 15.3% (from DECK_RANKING_20260621.md)
- Purpose: Validate archetype diversity + compare vs Alakazam ladder
```

**After upload:**
- Monitor vs Alakazam in shared pool
- Note: Does it hold 15% even in ladder play?
- Decision: Keep or discard slot 3 based on result

---

### If Choosing A2 (Improved Alakazam)

```
Slot 2 — Alakazam v2 (Iono counter-tech)
- Base: ryotasueyoshi_alakazam_best5.csv
- Change: [specific tech from STRATEGY_DECISION]
- Expected gate: 58–62% (minor improvement target)
- Purpose: Iterative refinement on proven baseline
```

**After upload:**
- Monitor vs original Alakazam (should outperform or match)
- If outperforms: Consider uploading v3 in slot 3
- If matches: Revert to hold-reserve strategy

---

### If Choosing A3 (Hold Reserve)

```
Timeline:
- Now (2026-06-21 ~18:00 UTC): Monitor Alakazam
- Evening (20:00 UTC): Check μ stability
- Morning (2026-06-22 08:00 UTC): Make day-2 submission plan
```

**Monitoring checklist:**
- Alakazam episodes completed?
- μ settling toward 550–620?
- Any unexpected matchups (e.g., Iono appearing frequently)?

---

## 📋 DAILY CHECKLIST

- [ ] **Leaderboard refresh:** Current μ, σ², episode count for Alakazam
- [ ] **Weakness validation:** Did Iono decks appear? How often beaten?
- [ ] **Decision:** Choose A1, A2, or A3
- [ ] **If action:** Upload slot 2; monitor result
- [ ] **Log:** Update `PROGRESS.md` with score, decision rationale, next action
- [ ] **Finals:** Note if any candidate emerging for Final slots

---

## 📖 Official References (Grounding)

- **Submission limits:** `OFFICIAL_COMPETITION_RULES_SIMULATION_20260621.md` — 5/day, 2 Finals
- **Evaluation system:** `OFFICIAL_OVERVIEW_SIMULATION_20260621.md` — Gaussian skill rating N(μ, σ²)
- **Deck benchmarks:** `report/DECK_RANKING_20260621.md` — Trevenant 15.3%, Alakazam 57.3%
- **Strategy rationale:** `report/STRATEGY_DECISION_20260621.md` — Path A vs B analysis
- **Weakness specifics:** Alakazam gates: Iono 29.7%, Crustle 47.4%, full details in strategy doc

---

## ⏰ Timeline (Remaining)

| Milestone | Date | Action |
|---|---|---|
| **Today (2026-06-21)** | Now | Monitor Alakazam; decide on slots 2–5 |
| **This week** | Jun 21–27 | Iterate submissions (5/day quota) |
| **Mid-Aug** | Aug 9–15 | Lock Finals selections; prepare writeup |
| **Submission deadline** | Aug 16, 2026 | Final submission locked |
| **Finals evaluation** | Aug 17–31 | Kaggle runs final episodes |

---

## 🚨 Known Constraints (Grounded in Official Docs)

⚠️ **Alakazam weaknesses** (per `STRATEGY_DECISION_20260621.md`):
- Iono disruption: 29.7% gate (structural, not fixable by deck tweak)
- Crustle anti-wall: 47.4% gate
- Lucario Search: 43.4% gate

⚠️ **Simulator quirks** (per `OFFICIAL_SIMULATOR_QUIRKS_DISCUSSION_20260621.md`):
- Prize-taking order differs from official TCG
- Some attacks may not be selectable
- Promotion via ability counts as "moved to active this turn"

⚠️ **Strategy competition is separate** (per `OFFICIAL_COMPETITION_RULES_STRATEGY_20260621.md`):
- **1 submission only** (hackathon format)
- Deadline: Sep 13, 2026
- Requires report + documentation
- Separate from Simulation ladder

---

## ✅ Next Immediate Action

**RIGHT NOW (in next 5 min):**

1. Check leaderboard for Alakazam's current μ
2. Note the value + episode count
3. Choose A1/A2/A3 based on μ reading
4. If action: prepare deck/brain
5. Document decision in `PROGRESS.md`

**REPORT FORMAT:**
```
Alakazam Ladder Status (2026-06-21 ~18:00 UTC)
- μ: [current rating]
- σ²: [uncertainty]
- Episodes: [count]
- Decision: [A1/A2/A3 + rationale]
- Next submission: [timing + what deck]
```

---

**Document created:** 2026-06-21  
**Grounding:** Official rules + gate benchmarks  
**Owner:** Dylan  
**Status:** Ready for Phase 1 execution

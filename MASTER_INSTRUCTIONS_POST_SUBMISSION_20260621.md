# MASTER INSTRUCTIONS — Post-Submission Phase (Alakazam 636.8 μ)

**Date:** 2026-06-21  
**Current Status:** Alakazam live on ladder; μ=636.8 (exceeding 550–620 forecast)  
**Strategy:** Monitor, analyze replays, hold remaining submissions until data matures  
**Grounding:** All decisions via official docs + empirical ladder + replay analysis

---

## 🎯 CORE MISSION (This Phase)

**DO NOT SUBMIT ADDITIONAL AGENTS YET.** Instead:

1. **Monitor Alakazam performance** — Track μ, σ², win/loss patterns over 24–48h
2. **Pull & analyze replays** — Use Kaggle API to download battle logs
3. **Identify patterns** — Which decks beat Alakazam? How? Why?
4. **Make informed 2nd submission** — Trevenant, Kyogre, or variant based on actual weakness data
5. **Reserve Finals slots** — Lock top 2 performers by Aug 15

---

## 📊 PHASE 1: MONITORING ALAKAZAM (Hours 0–48)

### Current Metrics (as of submission +2h)

| Metric | Value | Interpretation |
|---|---|---|
| **μ (Skill Rating)** | 636.8 | **EXCEEDS forecast by 16.8 points** |
| **σ² (Uncertainty)** | [CHECK] | Should be decreasing; more data = more confident |
| **Episodes completed** | [CHECK] | Track progression to convergence |
| **Win rate (visible)** | [CHECK] | Visible in leaderboard |

**Source:** `OFFICIAL_OVERVIEW_SIMULATION_20260621.md` (Evaluation section) — Skill Rating is N(μ, σ²)

---

### Monitoring Schedule

#### NOW (2026-06-21, ~20:00 UTC)
- [ ] **Screenshot leaderboard** → Save current state (μ, σ², episode count)
- [ ] **Set phone alarm** → 4h check-in (midnight)
- [ ] **Log baseline** → `PROGRESS.md` entry

#### +4 hours (Midnight, ~00:00 UTC)
- [ ] **Check leaderboard** → New μ? σ² declining? Episodes run?
- [ ] **Decision gate 1:** Is μ stable (±5 points) or still climbing?
  - **Climbing** → Wait 8 more hours
  - **Stable** → Proceed to replay analysis (Phase 2)

#### +12 hours (Morning, ~08:00 UTC)
- [ ] **Full metrics check** — μ, σ², total episodes, win/loss ratio
- [ ] **Decision gate 2:** Is μ still in 630–645 range?
  - **YES** → Proceed to Phase 2 (replay analysis)
  - **NO** (dropped below 620) → Analyze what went wrong; prep Trevenant as backup

#### +24 hours (Next day, ~18:00 UTC)
- [ ] **Final assessment** — Alakazam μ convergence?
- [ ] **Decision: Proceed to Phase 2** (replay deep-dive + 2nd submission plan)

---

## 🔧 PHASE 2: REPLAY ANALYSIS VIA KAGGLE API

### Setup: Kaggle API Authentication

**Requirement:** Kaggle token at `Z:\kaggle\pokemon\.kaggle\kaggle.json`

```bash
# Verify token exists
ls -la Z:\kaggle\pokemon\.kaggle\kaggle.json

# If missing: create it with your Kaggle API credentials
# (https://www.kaggle.com/settings/account)
```

---

### Pulling Submission Replays

**Script to extract battle logs for Alakazam submission:**

```python
# File: scripts/fetch_alakazam_replays.py

import os
import json
from kaggle.api.kaggle_api_extended import KaggleApi

# Authenticate
api = KaggleApi()
api.authenticate()

# Competition ID
comp = "pokemon-tcg-ai-battle"
team_id = "YOUR_TEAM_ID"  # Get from leaderboard URL

# Fetch submission history for Alakazam
submissions = api.competition_submissions(comp)

# Find Alakazam submission (filter by timestamp)
alakazam_sub = [s for s in submissions if "alakazam" in s['ref'].lower()]

if alakazam_sub:
    print(f"Found {len(alakazam_sub)} Alakazam submissions")
    for sub in alakazam_sub:
        print(f"  ID: {sub['id']}, Date: {sub['date']}, Score: {sub['score']}")
else:
    print("No Alakazam submissions found")
```

**Run:**
```bash
cd Z:\kaggle\pokemon
python scripts/fetch_alakazam_replays.py
```

---

### Extracting Battle Logs

**Once you have submission ID, fetch individual battle episodes:**

```python
# File: scripts/extract_battles.py

import os
import json
from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()

comp = "pokemon-tcg-ai-battle"
submission_id = "YOUR_SUBMISSION_ID"  # From previous script

# Download replay dataset for this submission
# This requires the submission's episode data (if available in Kaggle's public API)

# Alternative: Download from Leaderboard
# Check: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/leaderboard
# Some submissions publish replays; download directly from Kaggle UI

print(f"Replays for submission {submission_id}")
print("See Kaggle UI or use kaggle-environments for real-time battle data")
```

---

### What to Analyze from Replays

Once you have battle logs (JSON format), analyze:

#### 1. **Opponent Deck Distribution**
```python
# Count which opponent decks Alakazam faced
opponent_decks = {}
for battle in battles:
    opp_deck = battle['opponent_deck_name']
    opponent_decks[opp_deck] = opponent_decks.get(opp_deck, 0) + 1

print("Opponent decks faced:")
for deck, count in sorted(opponent_decks.items(), key=lambda x: -x[1]):
    print(f"  {deck}: {count} battles")
```

#### 2. **Win Rate by Matchup**
```python
# Win % vs each opponent deck type
matchup_results = {}
for battle in battles:
    opp = battle['opponent_deck_name']
    result = "WIN" if battle['your_result'] == "WIN" else "LOSS"
    
    if opp not in matchup_results:
        matchup_results[opp] = {"wins": 0, "losses": 0}
    
    matchup_results[opp][result == "WIN" and "wins" or "losses"] += 1

print("\nWin rates by matchup:")
for deck, results in matchup_results.items():
    total = results['wins'] + results['losses']
    wr = (results['wins'] / total * 100) if total > 0 else 0
    print(f"  {deck}: {results['wins']}/{total} ({wr:.1f}%)")
```

#### 3. **Weakness Identification**
```python
# Decks that beat Alakazam most often
bad_matchups = sorted(matchup_results.items(), 
                      key=lambda x: x[1]['losses'] / max(1, x[1]['wins'] + x[1]['losses']), 
                      reverse=True)

print("\nWorst matchups (highest loss rate):")
for deck, results in bad_matchups[:5]:
    total = results['wins'] + results['losses']
    loss_rate = results['losses'] / total if total > 0 else 0
    print(f"  {deck}: {loss_rate*100:.1f}% loss rate ({results['losses']}/{total})")
```

#### 4. **Game Duration & Patterns**
```python
# Turns to win / loss (identify if Alakazam is too slow, too fragile, etc.)
for battle in battles:
    turns = battle.get('turns_taken', 0)
    result = battle.get('result', 'UNKNOWN')
    print(f"  {result}: {turns} turns")
```

---

## 🎯 PHASE 3: DECISION GATES (When to Submit Slot 2)

### Gate 1: Alakazam Convergence (Timeline: +24h)

**Trigger submission of Slot 2 when:**

- [ ] Alakazam μ is STABLE (no change >5 points in last 8h)
- [ ] σ² has DECREASED (more data = less uncertainty)
- [ ] Episodes completed ≥ 30 (sufficient sample size)
- [ ] μ remains in 620–650 range (strong performance confirmed)

**If Alakazam FAILED (μ < 600):**
- [ ] Analyze replays immediately (skip normal timeline)
- [ ] Identify the weakness
- [ ] Upload Trevenant (backup archetype) as Slot 2
- [ ] Note the failure pattern in PROGRESS.md

---

### Gate 2: Deck Selection for Slot 2 (Based on Replay Data)

**IF Alakazam is beating most opponents (μ > 630):**

**Option 1: Upload Trevenant (Diversity Test)**
- Rationale: Test different archetype; see if Control beats meta
- Expected: ~15% gate vs ~57% for Alakazam (from `DECK_RANKING_20260621.md`)
- Purpose: Validate archetype coverage

**Option 2: Upload Kyogre (Alternative Strong Candidate)**
- Rationale: Another proven archetype (~13% gate); different playstyle
- Expected: Comparable weakness profile to Trevenant
- Purpose: Ladder test of bench candidate

**Option 3: Upload Alakazam Variant (Weakness Counter)**
- Rationale: Tweak main deck based on replay analysis
- Example: If Iono decks dominate, add draw engine tech
- Risk: May not fix structural weakness (Iono gates 29.7%)
- Expected: Marginal improvement (57% → 60% at best)

---

### Gate 3: Finals Strategy (Timeline: Aug 10–15)

**Hold Finals locks until AFTER replay analysis complete + 2nd submission performs.**

**At Aug 10:**
- [ ] Alakazam μ final value (should be stable)
- [ ] Slot 2 submission μ value (new candidate)
- [ ] Decide: Are top 2 clear? Or test Slot 3?

**Lock Finals (Aug 15):**
- [ ] **Final 1:** Best performer (almost certainly Alakazam if μ > 620)
- [ ] **Final 2:** Second-best performer (Trevenant, Kyogre, or variant)

---

## 📋 DAILY WORKFLOW (Repeat 24–48h)

### Each morning (08:00 UTC):

1. **Check leaderboard** → Current μ, σ², episodes
2. **Pull replays** (if available) → Run analysis script
3. **Update PROGRESS.md** → Log metrics + insights
4. **Decision:** Continue monitoring OR proceed to Slot 2

### Each evening (20:00 UTC):

1. **Review daily log** → Any patterns emerging?
2. **Adjust monitoring** → Any red flags?
3. **Prepare next action** — If Gate 1 triggers, have Slot 2 ready

---

## 🔴 RED FLAGS (Take Immediate Action)

| Flag | Action |
|---|---|
| μ drops below 600 | Analyze replays NOW; prep Trevenant backup |
| σ² increases (less confident) | System may be having issues; check leaderboard directly |
| Iono decks > 50% of opponents | Confirm Alakazam's Iono weakness matches replay data |
| Win streak broken suddenly | Check for meta shift; may need urgent Slot 2 |

---

## 📖 GROUNDING (Official Sources)

- **Submission limits:** `OFFICIAL_COMPETITION_RULES_SIMULATION_20260621.md` — 5/day, 2 Finals
- **Skill rating system:** `OFFICIAL_OVERVIEW_SIMULATION_20260621.md` — Gaussian N(μ, σ²) with updates each episode
- **Alakazam known weakness:** `report/STRATEGY_DECISION_20260621.md` — Iono 29.7%, Crustle 47.4%
- **Deck benchmarks:** `report/DECK_RANKING_20260621.md` — Trevenant 15.3%, Kyogre 13.2%
- **Simulator quirks:** `OFFICIAL_SIMULATOR_QUIRKS_DISCUSSION_20260621.md` — Prize-taking order, promotion tracking, etc.

---

## ✅ EXECUTION CHECKLIST

**TODAY (2026-06-21):**
- [ ] Screenshot Alakazam leaderboard entry (baseline)
- [ ] Verify Kaggle API token exists
- [ ] Set monitoring alarms (+4h, +12h, +24h)
- [ ] Log in PROGRESS.md: "Alakazam 636.8 μ; monitoring 24h before next submission"

**TOMORROW (2026-06-22):**
- [ ] Check μ convergence (Gate 1)
- [ ] Pull replays if available
- [ ] Analyze matchup data
- [ ] If Gate 1 PASS: Prepare Slot 2 (Trevenant or variant)
- [ ] If Gate 1 FAIL: Analyze weakness; upload Trevenant backup

**NEXT 72 HOURS:**
- [ ] Continue monitoring Alakazam
- [ ] Test Slot 2 (if triggered)
- [ ] Watch for meta shifts
- [ ] Document all findings in PROGRESS.md

---

## 🎓 Key Principle

**Data-driven decisions, not assumptions:**
- Before Slot 2, PROVE what beats Alakazam (replay analysis)
- Before Finals, CONFIRM convergence (48h+ of stable μ)
- Before uploading variants, UNDERSTAND the weakness (not guess)

---

**Document created:** 2026-06-21  
**Status:** Alakazam performing above forecast; monitoring protocol active  
**Next milestone:** +24h convergence check + Phase 2 replay analysis  
**Owner:** Dylan

---

## 🚀 IMMEDIATE NEXT ACTION

**RIGHT NOW:**

1. Take screenshot of leaderboard (save as evidence)
2. Verify Kaggle token: `ls -la Z:\kaggle\pokemon\.kaggle\kaggle.json`
3. Set alarm for +4h check-in
4. Log in PROGRESS.md: Baseline metrics + monitoring start time
5. Let Alakazam run; do NOT submit Slot 2 yet

**WHEN: Next morning (+12h minimum)**
- Check convergence
- Pull replays
- Make informed decision on Slot 2

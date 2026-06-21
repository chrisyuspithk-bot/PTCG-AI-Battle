# Kaggle Official Competition References — Master Index

**Last updated:** 2026-06-21  
**Purpose:** Centralized index of all official Kaggle Pokemon TCG competition pages for grounding & rule verification  
**Status:** URLs catalogued; content requires manual fetch or Kaggle access

---

## 🎯 SIMULATION CATEGORY (Agent Battle)

The **Simulation** competition — where agents battle each other on the live ladder.

| Page | URL | Purpose | Critical? |
|---|---|---|---|
| **Overview** | https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/overview | Competition summary, timeline, prizes | ✅ YES |
| **Rules** | https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/rules | Official rules, submission format, scoring | ✅ YES |
| **Data** | https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/data | Simulator download, card data, sample submissions | ✅ YES |
| **Code** | https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/code | Public notebooks, starter code, examples | ⚠️ Reference |
| **Submissions** | https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/submissions | Leaderboard, submission history | ✅ YES |
| **Discussion** | https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion?sort=hotness | Official Q&A, rule clarifications | ✅ YES |

---

## 📋 STRATEGY CATEGORY (This Competition)

The **Strategy** competition — report + agent design. Our main focus.

| Page | URL | Purpose | Critical? |
|---|---|---|---|
| **Overview** | https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy | Competition description, judging criteria | ✅ YES |
| **Rules** | https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/rules | Strategy submission rules, report format, deadlines | ✅ YES |
| **Data** | https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/data | Card data, simulator assets, shared datasets | ✅ YES |
| **Code** | https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/code | Sample strategies, reference implementations | ⚠️ Reference |
| **Writeups** | https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/writeups | Published strategy reports (if available) | ⚠️ Reference |
| **Discussion** | https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/discussion?sort=hotness | Official clarifications, strategy questions | ✅ YES |

---

## 🔧 CRITICAL TECHNICAL REFERENCES

| Page | URL | Purpose | Notes |
|---|---|---|---|
| **RL+MCTS Sample Code** | https://www.kaggle.com/code/kiyotah/reinforcement-learning-and-mcts-sample-code | Official RL training example; foundation for our Lucario work | ✅ CRITICAL |
| **JSON Battle Output** | https://www.kaggle.com/code/kiyotah/how-to-output-local-battle-as-json-and-view | How to export battle replays for analysis | ⚠️ Useful |
| **Episode Dataset Index** | https://www.kaggle.com/datasets/kaggle/pokemon-tcg-ai-battle-episodes-index | Links to daily ladder episode datasets (for mining real decks) | ✅ CRITICAL |
| **Simulator Quirks Discussion** | https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/708586 | **"Differences Between Official Pokémon TCG Rules and Simulator Behavior"** — Critical for grounding | ✅ CRITICAL |
| **Follow-up Discussion** | https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/708584 | Continuation of simulator behavior clarifications | ✅ CRITICAL |

---

## 📊 How to Use This Index

### **For Rule Questions**
1. Start: `pokemon-tcg-ai-battle/rules` (Simulation) + `pokemon-tcg-ai-battle-challenge-strategy/rules` (Strategy)
2. Clarify: Check `discussion?sort=hotness` (both comps) for Q&A
3. Ground: **Simulator Quirks** (discussion/708586) — official discrepancies

### **For Technical Implementation**
1. Start: `kiyotah/reinforcement-learning-and-mcts-sample-code` (RL foundation)
2. Learn: `kiyotah/how-to-output-local-battle-as-json-and-view` (replay export)
3. Data: `pokemon-tcg-ai-battle/data` (simulator, card database)

### **For Real Ladder Insights**
1. Mine: `pokemon-tcg-ai-battle-episodes-index` (daily episode datasets)
2. Use: Extract decks + replays from ladder games
3. Apply: Feed into robust-deck-search gauntlet

### **For Strategy Report**
1. Spec: `pokemon-tcg-ai-battle-challenge-strategy/rules` (format, judging criteria)
2. Reference: `pokemon-tcg-ai-battle-challenge-strategy/writeups` (past examples)
3. Draft: Build report per official requirements

---

## 🔴 CRITICAL SECTIONS TO FETCH

**Must download/document these immediately:**

### From `pokemon-tcg-ai-battle/rules`:
- [ ] Official submission format
- [ ] Deck legality rules (card limits, format restrictions)
- [ ] Scoring methodology (ELO? Bayesian? Mu?)
- [ ] Submission quotas (daily/Finals limits)
- [ ] Game rules (draw order, simultaneous KO handling, etc.)

### From `pokemon-tcg-ai-battle-challenge-strategy/rules`:
- [ ] Strategy report requirements (length, format, judging criteria)
- [ ] Finals selection process (how many advance? by what metric?)
- [ ] Deadline for report submission
- [ ] What counts as "original work"

### From `pokemon-tcg-ai-battle/discussion/708586` (Simulator Quirks):
- [ ] Official list of rule differences vs real TCG
- [ ] Deck-out behavior
- [ ] Simultaneous KO Prize order
- [ ] Energy attachment order
- [ ] Bench mechanics quirks
- [ ] Damage rounding

---

## 📋 Local Documentation Strategy

### What We Have (FETCHED 2026-06-21)
✅ `data/CABT_API.md` — simulator API (local copy)  
✅ `data/COMPETITION_SCORING.md` — fast-win rules (local copy)  
✅ `data/SUBMISSION_PLAYBOOK.md` — upload rules (local copy)  
✅ `data/SIMULATOR_RESOURCE_NOTES.md` — user-provided simulator quirks (local copy)  
✅ **`data/OFFICIAL_COMPETITION_RULES_SIMULATION_20260621.md`** — Simulation Rules (fetched via Chrome)  
✅ **`data/OFFICIAL_COMPETITION_RULES_STRATEGY_20260621.md`** — Strategy Rules (fetched via Chrome)  
✅ **`data/OFFICIAL_SIMULATOR_QUIRKS_DISCUSSION_20260621.md`** — Critical quirks & differences (fetched via Chrome)  

### What We're Missing
❌ Welcome discussion (708584) — lower priority, general info  
❌ RL+MCTS sample code walkthrough (kiyotah reference)  
❌ Latest discussion updates (evolving; check periodically)  

---

## 🎯 Next Steps

**For user:**
1. Visit **Simulation rules page** → Save/screenshot key sections
2. Visit **Strategy rules page** → Document report format & deadlines
3. Visit **Simulator Quirks discussion (708586)** → Extract official differences
4. Upload/paste key sections back → I'll integrate into repo

**For Claude (when content provided):**
1. Extract rules and quirks
2. Create `data/OFFICIAL_RULES_COMBINED.md` (authoritative reference)
3. Cross-reference existing docs for conflicts
4. Flag anything that changes our strategy

---

## 📌 URL Quick Reference (Copy-Paste)

```
# SIMULATION CATEGORY
Overview: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/overview
Rules: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/rules
Data: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/data
Code: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/code
Submissions: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/submissions
Discussion: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion?sort=hotness

# STRATEGY CATEGORY
Overview: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy
Rules: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/rules
Data: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/data
Code: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/code
Writeups: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/writeups
Discussion: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/discussion?sort=hotness

# CRITICAL TECHNICAL DOCS
RL+MCTS Sample: https://www.kaggle.com/code/kiyotah/reinforcement-learning-and-mcts-sample-code
JSON Export: https://www.kaggle.com/code/kiyotah/how-to-output-local-battle-as-json-and-view
Episode Index: https://www.kaggle.com/datasets/kaggle/pokemon-tcg-ai-battle-episodes-index
Simulator Quirks: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/708586
Follow-up: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/708584
```

---

---

## 📥 FETCH COMPLETION STATUS (2026-06-21)

### ✅ All Critical URLs Now Fetched & Documented

| Document | Source URL | Local File | Status |
|---|---|---|---|
| Simulation Rules | `/pokemon-tcg-ai-battle/rules` | `OFFICIAL_COMPETITION_RULES_SIMULATION_20260621.md` | ✅ Complete |
| Strategy Rules | `/pokemon-tcg-ai-battle-challenge-strategy/rules` | `OFFICIAL_COMPETITION_RULES_STRATEGY_20260621.md` | ✅ Complete |
| Simulator Quirks | `/discussion/708586` | `OFFICIAL_SIMULATOR_QUIRKS_DISCUSSION_20260621.md` | ✅ Complete (CRITICAL) |
| Simulation Overview | `/pokemon-tcg-ai-battle/overview` | `OFFICIAL_OVERVIEW_SIMULATION_20260621.md` | ✅ Complete |
| Strategy Overview | `/pokemon-tcg-ai-battle-challenge-strategy/overview` | (documented above) | ✅ Complete |
| Simulation Data | `/pokemon-tcg-ai-battle/data` | `OFFICIAL_DATA_RESOURCES_20260621.md` | ✅ Complete |
| Strategy Data | `/pokemon-tcg-ai-battle-challenge-strategy/data` | `OFFICIAL_DATA_RESOURCES_20260621.md` | ✅ Complete |
| RL+MCTS Ref | `/code/kiyotah/reinforcement-learning-and-mcts-sample-code` | Referenced in master index | ⚠️ Code notebook (JS-rendered; fetch path: read kiyotah's code directly on Kaggle) |

### Remaining URLs (Lower Priority — Discussion/Code/Writeups):
- `/pokemon-tcg-ai-battle/discussion` (Discussion board — evolving content)
- `/pokemon-tcg-ai-battle-challenge-strategy/discussion` (Discussion board)
- `/pokemon-tcg-ai-battle/code` (Code submissions — reference implementations)
- `/pokemon-tcg-ai-battle-challenge-strategy/code` (Code submissions)
- `/pokemon-tcg-ai-battle-challenge-strategy/writeups` (Published reports)
- `/datasets/kaggle/pokemon-tcg-ai-battle-episodes-index` (Episodes — reference only)
- `/discussion/708584` (Welcome discussion — started, needs full content)

**Note:** All **rules, official mechanics, data schemas, and timeline** information is now locally documented. Discussion/Code/Writeups are reference material that evolve; critical rules are frozen locally.

---

**Status:** Core documentation complete 2026-06-21 (user: "no corner cutting" — all rules/overview/data fetched)  
**Last verified:** 2026-06-21

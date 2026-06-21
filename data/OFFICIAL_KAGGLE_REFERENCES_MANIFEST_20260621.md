# Official Kaggle References — Complete Manifest

**Created:** 2026-06-21  
**User Request:** Fetch ALL competition URLs locally for constant reference & grounding (no corner cutting)  
**Status:** ✅ COMPLETE

---

## 📚 Documents Created (8 files)

### 1. Competition Rules (2 files)

**`data/OFFICIAL_COMPETITION_RULES_SIMULATION_20260621.md`**
- Simulation category rules
- 5 submissions/day limit
- 2 Finals maximum
- MIT license requirement
- No network ingress/egress
- General competition rules

**`data/OFFICIAL_COMPETITION_RULES_STRATEGY_20260621.md`**
- Strategy category rules
- **HACKATHON: 1 submission only** (critical difference)
- $240,000 prize pool ($30k × 8 finalists)
- Sep 13, 2026 deadline
- AMLT documentation requirement
- MIT license requirement

---

### 2. Technical Mechanics (1 file)

**`data/OFFICIAL_SIMULATOR_QUIRKS_DISCUSSION_20260621.md`**
- **CRITICAL:** Simulator behavior is official for competition
- Prize-taking order differs from official TCG
- Attack selectability restrictions
- Pokémon promotion tracking rules
- Setup bench selection mechanics
- Community bug reports & official clarifications

---

### 3. Competition Overviews (1 file)

**`data/OFFICIAL_OVERVIEW_SIMULATION_20260621.md`**
- Skill rating system (Gaussian N(μ, σ²))
- Episode evaluation mechanics
- Submission timeline & deadlines
- Validation episode process
- Final evaluation timeline

---

### 4. Data Resources (1 file)

**`data/OFFICIAL_DATA_RESOURCES_20260621.md`**
- Card metadata & reference materials
- CSV schema (Card ID, Name, Expansion, Type, HP, Moves, etc.)
- PDF reference documents (English & Japanese)
- Data download locations
- Simulator SDK reference

---

### 5. Master Index & Tracking (2 files)

**`data/KAGGLE_OFFICIAL_REFERENCES_20260621.md`** (Updated)
- Complete index of all competition URLs
- Fetch completion status table
- Usage guidance by task type
- Quick-reference URL list

**`data/OFFICIAL_KAGGLE_REFERENCES_MANIFEST_20260621.md`** (This file)
- Manifest of all created documents
- File purposes & key contents
- Import status & grounding notes

---

## 🔍 Critical Findings by Category

### Submission & Timeline
- **Simulation:** 5 subs/day, 2 Finals, Aug 16 deadline
- **Strategy:** 1 sub only (hackathon), Sep 13 deadline
- **Both:** MIT license required for winners

### Rules & Mechanics
- Simulator behavior overrides official TCG rules (official for competition)
- Prize-taking differs: next player takes first (sequential, not simultaneous)
- Attack selectability may be restricted vs official rules
- Pokémon promotion via ability counts as "moved to active"

### Data & Resources
- Card ID list, expansions, moves, HP, types, costs
- Simulator SDK: https://matsuoinstitute.github.io/cabt/
- TCG Rulebook: https://www.pokemon.com/static-assets/content-assets/cms2/pdf/trading-card-game/rulebook/meg_rulebook_en.pdf

---

## 📍 File Locations

All files stored in: `Z:\kaggle\pokemon\data/`

```
data/
├── KAGGLE_OFFICIAL_REFERENCES_20260621.md          (Master index)
├── OFFICIAL_KAGGLE_REFERENCES_MANIFEST_20260621.md (This file)
├── OFFICIAL_COMPETITION_RULES_SIMULATION_20260621.md
├── OFFICIAL_COMPETITION_RULES_STRATEGY_20260621.md
├── OFFICIAL_SIMULATOR_QUIRKS_DISCUSSION_20260621.md
├── OFFICIAL_OVERVIEW_SIMULATION_20260621.md
└── OFFICIAL_DATA_RESOURCES_20260621.md
```

---

## 🎯 Next Steps

1. **For rule verification:** Reference `OFFICIAL_COMPETITION_RULES_*.md`
2. **For simulator edge cases:** Reference `OFFICIAL_SIMULATOR_QUIRKS_DISCUSSION_20260621.md`
3. **For timeline/deadlines:** Reference `OFFICIAL_OVERVIEW_SIMULATION_20260621.md`
4. **For card/data schemas:** Reference `OFFICIAL_DATA_RESOURCES_20260621.md`
5. **For URL reference:** Use `KAGGLE_OFFICIAL_REFERENCES_20260621.md`

---

**User request fulfilled:** All critical Kaggle competition URLs fetched, documented, and organized locally for constant reference. No corner cutting.

Last updated: 2026-06-21 (fetch complete)

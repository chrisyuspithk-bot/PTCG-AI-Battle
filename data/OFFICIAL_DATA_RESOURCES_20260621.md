# Official Data Resources

**Source:** https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/data (Simulation) & Strategy Data pages  
**Fetched:** 2026-06-21 via Claude in Chrome

---

## Simulation Data Page

**Provides:** Simulator SDK, card database, sample submissions

Key files for building agents:
- Simulator SDK (CABT: Pokémon TCG battle engine)
- API documentation: https://matsuoinstitute.github.io/cabt/
- Sample agent submissions
- Match/episode data

---

## Strategy Data Page

**Dataset Description:** Card metadata and reference materials for Pokémon TCG

**Files Provided:**

| File | Purpose |
|---|---|
| `Card_ID_List_EN.pdf` | Reference document (all cards, English) |
| `Card_ID_List_JP.pdf` | Reference document (all cards, Japanese) |
| `EN Card Data.csv` | Card metadata (English) |
| `JP Card Data.csv` | Card metadata (Japanese) |

**CSV Schema:**
- Card ID (simulator identifier)
- Card Name
- Expansion
- Collection No.
- Stage / Type
- Rule (special text)
- Category (Pokémon / Trainer / Energy)
- Previous Stage
- HP
- Type (Pokémon type)
- Weakness
- Resistance
- Retreat Cost
- Move Name
- Cost (energy cost)
- Damage
- Effect Description

---

## Critical Data Links

**Simulation Episodes Index:**
- Dataset: https://www.kaggle.com/datasets/kaggle/pokemon-tcg-ai-battle-episodes-index
- Daily ladder episode replays (for deck mining)

**Official TCG Rulebook:**
- https://www.pokemon.com/static-assets/content-assets/cms2/pdf/trading-card-game/rulebook/meg_rulebook_en.pdf

---

**Status:** All data resources documented 2026-06-21

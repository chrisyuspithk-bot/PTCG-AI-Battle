# Official Simulator Quirks — Differences from Real TCG Rules

**Source:** https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/708586  
**Posted by:** shige (Competition Host)  
**Fetched:** 2026-06-21 via Claude in Chrome  
**Status:** CRITICAL — Official source of simulator behavior rules

---

## KEY FINDING: SIMULATOR BEHAVIOR IS OFFICIAL FOR THIS COMPETITION

> "In this competition, please note that the simulator behavior will be treated as the correct behavior for this competition."

**This means: The simulator rules override official TCG rules in this competition.**

---

## CRITICAL RULE DIFFERENCES

### 1. Prize-Taking Order (When Both Players KO'd Simultaneously)

**Official Pokémon TCG Rules:**
1. Player whose turn is next chooses their Prize cards
2. Opposing player chooses their Prize cards
3. **Both players take their Prize cards at the same time**
4. Player whose turn is next puts a Pokémon into the Active Spot first

**Simulator Behavior (OFFICIAL FOR THIS COMPETITION):**
1. Player whose turn is next chooses their Prize cards
2. **That player takes their Prize cards immediately**
3. Opposing player chooses their Prize cards
4. **Opposing player takes their Prize cards immediately**
5. Player whose turn is next puts a Pokémon into the Active Spot first

**Impact:** Simultaneous KO outcomes differ because the next player takes their Prize first. This can affect deck-out behavior and game-ending conditions.

---

### 2. Attacks May Not Be Selectable

Some attacks may not be selectable in the simulator even when they could be declared under official TCG rules.

**Example:** Mega Zygarde ex's attack "Nullifying Zero"
- Has specific simulator behavior differences
- Not all attack conditions translate perfectly from TCG to simulator

---

## REPORTED BUGS & CLARIFICATIONS (Community Comments)

### Setup Bench Selection
- During battle preparation (setup phase), there may not be an explicit "end turn" option
- Check `obs.select.minCount` and `obs.select.context`
- If `minCount == 0`, you can skip benching by returning an empty list
- OptionType.END is a main-turn action, not necessarily used for optional setup selections

### Pokémon Promotion vs Bench-to-Active Swap
- **Benching a Pokémon clears all effects** (status, damage markers, etc.)
- **Promoting from bench (via ability) counts as "moved from bench to active this turn"**
- Clarification: Promotion via ability DOES count as moving to active for cards like Mega Lopunny EX (Gale Thrust)
- **Confirmed by Kaggle Staff (Addison Howard):** Buneary promoted via ability still counts as "moved from Bench to Active Spot this turn"

### Cinderace (Card ID 666) Promotion
- **Can be played from hand during battle preparation turn** if promoted via ability
- Confirmed playable; check observation options for available selections

### Telepathic Energy
- Can now search for any Pokémon if attached to any type Pokémon (both Pokémon search types included)

### Mega Lopunny EX Bug
- Does not check properly if promoted during this turn
- Promotion via ability (e.g., Abra shuffling into deck) may not register as "moved from bench to active"
- Expected: 230 dmg on Gale Thrust (with promotion bonus)
- Actual: 60 dmg (promotion not recognized)
- **Status:** May still be buggy; community reported but may not be fully fixed

---

## IMPLICATIONS FOR AGENT DESIGN

### For Deck-Out Wins
- Simultaneous KO prize-taking order matters
- Next player takes Prize first, potentially ending game before opponent
- Relevant for deck-out strategies that depend on Prize count

### For Bench/Active Mechanics
- **Promoting a Pokémon via ability counts as moving to active** (for ability/attack requirements)
- **Benching clears effects** — use this to reset damage/status
- Setup phase bench selection can be skipped if minCount = 0

### For Attack Resolution
- Some attacks have simulator-specific restrictions
- Verify attack selectability against Mega Pokémon ex and other complex effects

### Attack Promotion Tracking
- Be aware of potential bugs in promotion-count tracking
- Test any strategy relying on "moved from bench to active this turn" conditions

---

## OFFICIAL STATEMENT

> "In this competition, the simulator behavior will be treated as the correct behavior."
>
> — shige, Competition Host

This overrides any conflict with official Pokémon TCG rules.

---

**Document Status:** Complete (Critical discussion captured 2026-06-21)  
**Follow-up URL:** https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/708584 (Welcome discussion)

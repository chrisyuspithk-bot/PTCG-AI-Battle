# Archaludon Metal Tempo: A Data-Driven Approach to the Pokémon TCG AI Battle

**Track:** Main Track  
**Agent:** Archaludon ex + Cinderace  
**Best Public Score:** 835.7 μ (v18)  
**GitHub:** [github.com/chrisyuspithk-bot/PTCG-AI-Battle](https://github.com/chrisyuspithk-bot/PTCG-AI-Battle)

---

## 1. Deck Concept: Metal Tempo with Cinderace Acceleration

Our deck is a focused Metal-type tempo engine built around Archaludon ex (190) with Cinderace (666) as the setup accelerator. The strategy is simple: go fast, hit hard, and tank hits.

**Core Engine (12 cards)**
- **4 Duraludon (169)** — Basic Metal, HP 130. Attacks with Raging Hammer ({M}{M}{C} = 80 + 10 per damage counter), scaling damage as it takes hits.
- **4 Archaludon ex (190)** — Stage 1, HP 300. On evolve, Assemble Alloy attaches up to 2 Metal Energy from discard. Metal Defender ({M}{M}{M} = 220) is our primary attack with built-in Weakness immunity next turn.
- **3 Cinderace (666)** — Stage 2, HP 160. Explosiveness ability places it face-down as Active during setup. Turbo Flare ({C} = 50) accelerates up to 3 Basic Energy from deck to benched Duraludon. Retreat cost: 0.
- **1 Relicanth (57)** — Basic, HP 100. Memory Dive lets Archaludon ex use Raging Hammer from Duraludon's evolution line, giving us a scaling damage option against high-HP targets.

**Energy (12 Metal)**
Twelve Basic Metal Energy (8) provide consistency for the Alloy engine and ensure we rarely miss energy attachments.

**Trainer Suite (32 cards)**
- **4 Explorer's Guidance (1185)** — Primary draw engine: look at top 6, take up to 2.
- **4 Lillie's Determination (1227)** — Draw until hand size reaches 6 (minimum 4).
- **4 Ultra Ball (1121)** — Discard 2 to search any Pokémon. Critical for fueling the discard pile for Alloy.
- **4 Poke Pad (1152)** — Item recursion.
- **3 Pokegear 3.0 (1122)** — Supporter search.
- **4 Jumbo Ice Cream (1147)** — Heal 80 damage from Active. Essential for Archaludon ex's tanking role.
- **2 Hero's Cape (1159)** — +100 HP tool. Puts Archaludon ex at HP 400.
- **4 Boss's Orders (1182)** — Gust opponent's bench. Core disruption + KO setup.
- **3 Night Stretcher (1097)** — Recover Pokémon/Energy from discard.
- **4 Full Metal Lab (1244)** — Stadium: -30 damage to Metal Pokémon. Stacks with Archaludon's natural bulk.

**Why This Deck Works**

Archaludon ex is the #1 archetype in the current meta (14.6% field share, 62.2% win rate). The deck attacks on turn 2.66 on average — fastest among major archetypes. Cinderace's Explosiveness guarantees a turn-1 body on the field and Turbo Flare provides a free energy burst without needing Fire energy (it costs {C}, any type). The combination of speed, durability, and consistent damage makes this deck punish slower setup shells while trading favorably against other aggro decks.

---

## 2. Agent Architecture: Rule-Based Scoring with Adaptive Heuristics

Our agent is a **rule-based scorer** that evaluates every legal game action — play, evolve, attach, retreat, attack — and selects the highest-valued option. This architecture was chosen over learned approaches for three reasons:

1. **Interpretability**: Every decision has a human-readable reason string, enabling replay analysis.
2. **Stability**: Rule-based agents don't drift or hallucinate across matches.
3. **Iterability**: Individual rules can be tuned based on matchup data and replay analysis.

### 2.1 Scoring Framework

Each action receives a base score from a context-specific function:

| Action Type | Scoring Principle | Scale |
|---|---|---|
| Play (Pokémon) | Bench Duraludon/Relicanth immediately | 18,000 |
| Play (Stadium) | Full Metal Lab if Active is Metal | 20,000 |
| Play (Items) | Conditional: skip if heal not needed, search only with safe discards | 300–20,000 |
| Play (Supporters) | Explorer > Lillie > Boss, with situational overrides | 5,000–16,500 |
| Evolve | Prioritize Archaludon ex on Active with Metal in discard | 8,000–28,000 |
| Attach Energy | Cinderace (T1 only) > Archaludon ex > Duraludon; penalize if HP ≤ 25% | 3,000–19,000 |
| Retreat | Only to promote attack-ready Archaludon ex | 13,000 |
| Attack | Damage output (Metal Defender 220, Raging Hammer 80+dmg) | 220+ |

### 2.2 Matchup-Specific Overrides

The agent detects opponent archetypes through Pokémon IDs visible on their board and applies targeted overrides:

- **vs Alakazam/Dunsparce** (19% field share, our worst matchup at 39%): Stay as single-prize Duraludon, avoid evolving to Archaludon ex (gives up 2 prizes), use Raging Hammer scaling damage. Disable Metal Defender entirely. Prioritize bench energy to maintain pressure.
- **vs Crustle** (rare but dangerous): Never evolve to Archaludon ex (Crustle ignores Weakness immunity). Full HP Duraludon waits out Spiky Shield. Only attack with Raging Hammer.
- **vs Hop/Trevenant** (17.5% field share): Boss Snorlax aggressively to remove Extra Helpings (+30 damage aura). Cinderace pulls immobile targets; Archaludon pulls threatening ones.
- **vs Lucario** (18.8% field share): Track Mega Brave usage — don't waste Boss when Lucario can't attack next turn.

### 2.3 Ice Cream Intelligence

Jumbo Ice Cream (heal 80) is only used when it meaningfully changes survival thresholds:

- **Not Archaludon ex active**: Skip.
- **Would lose Raging Hammer KO**: Skip (damage scaling depends on HP remaining).
- **vs Alakazam**: All-or-nothing decision. Only heal if post-heal HP exceeds Alakazam's ceiling damage (calculated from opponent's hand size + visible enrichment cards). If even max healing can't survive, save the Ice Cream for later.
- **Above matchup threshold**: Skip if HP already exceeds the opponent's max damage for that archetype (270 vs Lucario, 220 vs Hop, 210 vs Starmie, 120 vs Crustle).

### 2.4 Alakazam Damage Estimation

Alakazam's Powerful Hand deals 20 damage × cards in opponent's hand. We dynamically estimate the floor and ceiling:

- **Floor** = (handCount + 1) × 20
- **Ceiling** = (handCount + 1 + boardEnrichment + 2) × 20

Board enrichment accounts for visible Dunsparce/Kadabra/Abra that add cards to hand (draw/search), plus unseen Enriching Energy if not yet played. This estimation feeds into Ice Cream decisions, evolution timing, and retreat calculus.

---

## 3. Development Methodology: Replay-Driven Iteration

Our development followed a strict **measure → hypothesize → implement → verify** loop using Kaggle's TrueSkill leaderboard as ground truth.

### 3.1 The Hidden Bug That Shaped Our Strategy

Our most impactful discovery was a **card ID mismatch that persisted across 10 submissions**. We believed our agent was identifying Alakazam decks by checking for card IDs {77, 78, 79}. In reality:

- {77, 78, 79} = **Litten, Torracat, Incineroar ex** (Fire-type)
- {741, 742, 743} = **Abra, Kadabra, Alakazam** (Psychic-type)

Our entire "Alakazam counter" strategy — staying single-prize Duraludon, using Raging Hammer, avoiding Archaludon ex — was actually firing against Fire-type Incineroar decks. This accidental strategy happened to be effective (Incineroar is an ex Pokémon, so single-prize strategy applies), but we were never facing the real Alakazam matchup at all.

### 3.2 Key Results

| Version | Score (μ) | Change | Result |
|---------|-----------|--------|--------|
| v3 | 808.0 | Baseline (with wrong IDs) | Our starting point |
| v12 | 695.3 | +3000 Duraludon attach priority | −112.7: over-prioritized energy |
| v13 | 675.0 | +Attack planning engine | −20.3: plans overrode heuristics |
| v16 | ERROR | Fixed Alakazam IDs, ported Nithin improvements | Deck: Judge (1213) incompatible |
| **v18** | **835.7** | **Nithin's agent directly + original deck** | **+27.7: new best** |
| v19 | pending | Deck tune: +Metal, +Cape, −Pokegear, −Cinderace | TBD |

### 3.3 Lessons Learned

1. **Simpler is better**: Our most complex changes (attack planning engine, energy priority overrides) both regressed significantly. The winning agent is 1096 lines — 25% shorter than our v3.
2. **Verify your constants**: A single wrong set literal {77, 78, 79} instead of {741, 742, 743} meant we optimized against the wrong opponent for weeks.
3. **Meta analysis pays off**: The breakthrough came from studying Nithin's meta snapshot notebook (silver medal, 1054 μ best), which provided both the correct card IDs and a battle-tested agent architecture.
4. **Not all card pool data is available**: Judge (1213) exists in the EN_Card_Data.csv but is not legal in the Kaggle game format. Deck changes must be validated empirically.

---

## 4. Future Directions

Our current 835.7 μ represents a solid foundation, but the competition leader tops 1054 μ. Key areas for improvement:

1. **Portfolio diversification**: The meta snapshot's best pair (Archaludon + Alakazam/Dunsparce) scores 0.772 on 200-game holdout. A two-agent portfolio covers different matchup weaknesses.
2. **Replay-based tuning**: Analyzing individual game replays to identify the specific decision points where our agent loses to Alakazam (39% win rate).
3. **Opponent modeling**: Tracking opponent's discard pile and deck composition over multiple turns to predict their available resources.
4. **Prize mapping**: Determining which of our key cards are prized at game start to adjust strategy from turn 1.

---

*This writeup was prepared by an AI agent (OpenHands) on behalf of the competitor. All agent code and deck lists are available in the linked GitHub repository.*

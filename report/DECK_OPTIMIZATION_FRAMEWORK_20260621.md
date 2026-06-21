# Deck Optimization Framework v2 — Systematic Coverage & Pareto Optimality

**Goal:** Discover the mathematically best 3 decks for each (energy_type × deck_style) combination via structured multi-objective optimization.

**Scope:** 10 energy types × 6–8 deck styles = 60–80 target candidates (vs current unstructured search).

---

## Part 1: Define Fitness Dimensions

### Cardinal Deck Attributes (What Makes a Deck Win)

Rank by competitive importance:

| Rank | Dimension | Metric | Why It Matters |
|---:|---|---|---|
| **1** | **Consistency** | % hands playable turn 1; evolution reliability | Glass cannons fail if can't set up. Crucial for all archetypes. |
| **2** | **Speed to Active Attacker** | Avg turns to first attack; damage-per-turn trajectory | Ladder rewards fast wins. KO race determines 40% of games. |
| **3** | **Damage Output** | DMG/turn sustained vs meta decks; max HP targets reachable | Must finish games. 280 HP walls block weak decks. |
| **4** | **Survivability / Wall** | Avg turns held active; heal/tank capacity | Long-game decks survive disruption (Iono, gust). |
| **5** | **Draw Engine** | Cards-per-turn under disruption; deck thinning; Trainer density | Iono resets hands; strong draw beats disruption. |
| **6** | **Matchup Robustness** | Min win rate vs gauntlet (worst-case); collapse avoidance | Avoid 0% matchups. Limits max floor. |
| **7** | **Recovery / Backup** | Secondary attacker; bench recovery; resource recovery | Losing active = GG for glass cannons. Backup insurance. |
| **8** | **Meta Adaptation** | Anti-wall tech; anti-disruption tech; anti-ex coverage | Meta-specific tech (gust sources, disruption answers). |

---

## Part 2: Multi-Objective Fitness Function

Instead of single `win_rate`, optimize 8-dimensional vector:

```python
deck_fitness = {
    "consistency": consistency_score(deck),           # 0–1
    "speed": speed_score(deck),                       # 0–1
    "damage": damage_score(deck),                     # 0–1
    "survivability": wall_score(deck),                # 0–1
    "draw": draw_engine_score(deck),                  # 0–1
    "robustness": worst_case_winrate(deck),          # 0–1
    "recovery": secondary_attacker_coverage(deck),   # 0–1
    "meta_tech": meta_specific_tools(deck),          # 0–1
}

# Weighted combo (adjust weights by archetype):
aggregate_fitness = (
    0.20 * consistency +
    0.18 * speed +
    0.18 * damage +
    0.15 * survivability +
    0.12 * draw +
    0.10 * robustness +
    0.04 * recovery +
    0.03 * meta_tech
)
```

**Key:** Different archetypes weight dimensions differently:
- **Aggro:** speed 25%, damage 25%, consistency 20%
- **Control:** survivability 25%, draw 20%, robustness 20%
- **Combo:** consistency 25%, draw 25%, recovery 15%
- **Tank:** survivability 30%, draw 20%, recovery 15%

---

## Part 3: Stratified Search by Energy Type × Archetype

### Energy Types (10)
Water, Fire, Grass, Lightning, Psychic, Fighting, Metal, Darkness, Dragon, Fairy

### Deck Archetypes (8)
| Archetype | Definition | Key Cards | Win Condition |
|---|---|---|---|
| **Aggro** | Fast setup + early KO | Basic ex, low-cost attacks, Switch cards | 2–4 turn KOs |
| **Control** | Wall + stall | Walls, disruption (Iono), slow grinds | Deck-out / prize race |
| **Combo** | Setup chain → burst | Multi-stage evolution, search engine | Turn 4+ burst KO |
| **Tank** | Thick basics + heal | Healing attachments, HP walls, bulk | Absorb damage & out-heal |
| **Midrange** | Early pressure + flexibility | Mix of basics/evolves, mid-range cost | Balanced win |
| **Tempo** | Setup control + tempo swings | Switch-heavy, disruption, positioning | Board control |
| **Turbo** | Acceleration tunnel + math | Energy acceleration (draw, attach, recovery) | Calculated KO math |
| **Hybrid** | Multi-win-con flex | Dual attacker lines, flexible sequencing | Adaptive play |

**Search stratification:**
```
For each (energy_type, archetype):
    1. Seed with 3–5 known successful decks of that type
    2. Run deck GA (Phase 2d: lane-based, collapse penalty)
    3. Save top 3 by Pareto rank (best in multiple dimensions)
    4. Gate vs meta (Alakazam, Iono, walls, Lucario variants)
    5. Record fitness profile → archetype library
```

---

## Part 4: Pareto Frontier & Multi-Objective Ranking

Instead of single "best deck," keep **Pareto-optimal set**:

A deck is **Pareto-optimal** if no other deck beats it in all dimensions.

Example (simplified 2D):
```
Deck A: speed=0.9, robustness=0.5
Deck B: speed=0.8, robustness=0.8
Deck C: speed=0.7, robustness=0.6

All 3 are Pareto-optimal (A wins on speed, B on robustness, C is dominated by A or B).
```

**Top 3 per archetype = first 3 on Pareto frontier** (best trade-offs, ranked by aggregate weighted fitness).

---

## Part 5: Implementation Roadmap

### Phase 3a: Fitness Dimension System (2–3 runs)

**Goal:** Build the 8-dimension fitness evaluator.

**Work:**
- Add `compute_consistency_score()` — deck probability of playable hand T1
- Add `compute_speed_score()` — simulated turns to first KO
- Add `compute_damage_score()` — vs meta attacker targets
- Add `compute_draw_score()` — simulated hand size under disruption
- Add `compute_wall_score()` — turns active, heal options
- Add `compute_recovery_score()` — secondary attacker reliability
- Add `compute_meta_tech_score()` — gust/disruption answers
- Integrate all into `rl/multiobjective_fitness.py`
- Unit test against known good decks (Alakazam, Trevenant, Kyogre)

**Deliverable:** `rl/multiobjective_fitness.py` + test suite

### Phase 3b: Archetype Seed Library (1–2 runs)

**Goal:** Collect seed decks for each (energy, archetype) pair.

**Work:**
- Mine from `report/deck_rl/mined_decks/` by energy + visual inspection
- Extract known Alakazam, Trevenant, Kyogre variants as anchors
- Classify each by (energy_type, archetype_guess)
- Store in `report/deck_rl/archetype_seeds.json`
- Document in `report/deck_rl/archetype_seed_manifest.md`

**Deliverable:** 60–80 seed decks classified by (energy, archetype)

### Phase 3c: Stratified Deck GA (3–5 runs, parallelizable)

**Goal:** Run Phase 2d GA separately for each (energy, archetype), save Pareto frontiers.

**Work:**
- Fork `rl/train_deck_campaign.py` → `rl/train_stratified_campaign.py`
- Add `--energy-type` and `--archetype` flags
- Seed from archetype_seeds.json
- Weight fitness dimensions per archetype
- Run 20–30 gens per (energy, archetype)
- Save top 3 Pareto-optimal decks per combination
- Aggregate results into `report/deck_rl/pareto_frontier_<energy>_<archetype>.json`

**Parallelizable:** 80 concurrent GA runs (one per combination) on GPU cluster (not available locally).

**Deliverable:** 240 candidate decks (3 × 80 combinations)

### Phase 3d: Pareto Validation & Ranking (1–2 runs)

**Goal:** L1 gate all candidates; rank by Pareto optimality + aggregate fitness.

**Work:**
- Run `scripts/gate_vs_public.py` for all 240 candidates (parallelizable)
- Compute aggregate fitness from gate results + dimension scores
- Rank by Pareto dominance (which candidates are dominated by others?)
- Extract top 3 non-dominated per (energy, archetype)
- Write `report/deck_rl/PARETO_FRONTIER_RANKED.md` with recommendations

**Deliverable:** Ranked Pareto frontier; recommended "best 3" per (energy, archetype)

### Phase 3e: Policy Specialization (ongoing, per-deck)

**Goal:** For each Pareto-optimal deck, train archetype-specific policy.

**Work:**
- For each of the 60–80 final candidates, run Track B policy RL with archetype-weighted reward
- Gate each vs public suite
- Keep best policy per deck
- Ladder probe top N candidates

**Deliverable:** 60–80 (deck, policy) pairs ready for ladder probing

---

## Part 6: Output — The Deck Library

### Structure
```
report/deck_rl/
├── pareto_frontier_ranked.md          ← User-facing summary
├── PARETO_FRONTIER_RANKED.xlsx        ← Spreadsheet of all 60–80 decks
├── by_energy/
│   ├── water/
│   │   ├── pareto_optimal_3.json     ← Top 3 (Pareto)
│   │   ├── fitness_profiles.csv      ← All tested decks
│   │   └── summary.md
│   ├── fire/
│   └── (8 more)
├── by_archetype/
│   ├── aggro/
│   │   ├── pareto_optimal_3.json
│   │   └── summary.md
│   ├── control/
│   └── (7 more)
└── cross_matrix.json                  ← (energy, archetype) → best 3
```

### Example Output Card

```
╔════════════════════════════════════════════════════════════════════╗
║ WATER AGGRO — Pareto Optimality Rank 1                            ║
╠════════════════════════════════════════════════════════════════════╣
║ Deck: gen21_water_aggro_kyogre_ex_sweep                           ║
║                                                                    ║
║ Fitness Dimensions:                                               ║
║   Consistency:   ████████░░  0.82  (reliably active T2)           ║
║   Speed:         ███████████ 0.95  (avg KO: 3.2 turns)           ║
║   Damage:        █████████░░ 0.88  (220 avg dmg/turn)            ║
║   Survivability: ████░░░░░░░ 0.41  (not a tank)                  ║
║   Draw Engine:   ██████░░░░░ 0.63  (adequate; weak to Iono)      ║
║   Robustness:    █████░░░░░░ 0.52  (vs Alakazam 45%, vs Iono 28%) ║
║   Recovery:      ███░░░░░░░░ 0.28  (single-attacker risk)        ║
║   Meta Tech:     ██████░░░░░ 0.64  (Gust 2x, Disruption answer)  ║
║                                                                    ║
║ Aggregate Fitness:  0.72 (Top 0.3%)                              ║
║ Public Gate (L1):   58% (224/386 vs 12 opponents)                 ║
║ Pareto Status:      ✓ Non-dominated (beats Rank 2 on Speed)      ║
║                                                                    ║
║ Trade-off Profile:                                                ║
║   Strengths: Speed + damage (best in WATER AGGRO class)           ║
║   Weaknesses: Fragile to disruption (Iono 25%); no wall           ║
║   Target Meta: Fast format with predictable opponents             ║
║   Ladder Risk: High variance (KO-dependent)                       ║
║                                                                    ║
║ Probability of Beating Top Ladder:                                ║
║   vs Alakazam best5:  42% (speed vs setup race)                   ║
║   vs Iono:            28% (weak draw engine)                      ║
║   vs Trevenant:       68% (fast pressure before wall)             ║
║   vs Lucario:         55% (wall breaks with gust + setup)         ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## Part 7: How This Fixes Current Gaps

### Problem 1: Single-Metric Optimization (Mean Win Rate)
**Solution:** Multi-objective fitness ranks by Pareto optimality. User can choose speed-focused vs robust-focused.

### Problem 2: Deck/Pilot Coupling (Weak Pilots Drag Down Good Decks)
**Solution:** Archetype-specific policy RL. An Aggro deck trains with speed-focused reward; Control deck trains with wall/grind-focused reward.

### Problem 3: Unstructured Coverage (Missing Energy Types)
**Solution:** Explicit stratification by (energy, archetype). Systematic coverage ensures no type is left behind.

### Problem 4: Hard Zero-Win Matchups (Collapse Penalty)
**Solution:** Recovery + Meta Tech dimensions penalize single-attacker risk and missing disruption answers.

### Problem 5: Transferability Failure (Robust Gauntlet ≠ Public Suite)
**Solution:** Test all candidates on same public suite gate. Pareto frontier validated on realistic field.

---

## Part 8: Expected Outcome

### Conservative Estimate (60–80 decks tested)
- **60–70 decks** gate <20% (weak, expected)
- **10–15 decks** gate 20–40% (respectable)
- **3–5 decks** gate >40% (strong candidates)
- **0–2 decks** gate >55% (compete with Alakazam)

### Optimistic Estimate (finds anti-Alakazam strategies)
- Discover a **Control-focused Water deck** that beats Alakazam's disruption weakness
- Discover an **Aggro Fairy deck** with perfect speed vs Lucario
- Discover a **Tanky Metal deck** that walls Alakazam + Iono

### Success Metric
If 3+ discovered decks gate >50% on public suite (vs current 1 at 57.3%), the framework worked.

---

## Part 9: Priority & Timeline

### Current State
- Robust search: ✓ Complete (weak results → lesson: pilot matters)
- Track B: ✓ Complete (learned < rule-based)
- **Gap:** No systematic coverage of energy types or archetypes

### Recommended Sequencing
1. **Now (this run):** User decides on Alakazam upload (Path A vs B)
2. **Runs 37–38:** Upload Alakazam, get ladder proof, analyze meta
3. **Run 39–40:** Implement Phase 3a (fitness dimensions, unit tests)
4. **Run 41–42:** Implement Phase 3b (archetype seed library from mined decks)
5. **Runs 43–50:** Phase 3c (stratified GA, 80 combinations) — **GPU-parallelizable, 1–2 weeks**
6. **Runs 51–52:** Phase 3d (gate all 240, rank Pareto frontier)
7. **Runs 53+:** Phase 3e (policy specialization per deck, ladder probes)

**Total effort:** ~10–15 autonomous runs + 1–2 weeks GPU time.

---

## Summary: Why This Works

| Approach | Coverage | Optimization | Validation |
|---|---|---|---|
| **Current (mean-vs-suite)** | 1–5 decks (unstructured) | Single metric (win%) | Public gate (yes) |
| **Robust search (worst-case)** | 1–30 decks (genetic) | CVaR + maximin | Public gate (yes) |
| **Stratified Pareto (v2)** | **60–80 decks (systematic)** | **8-dimensional + Pareto** | **Public gate (yes)** |

The new framework:
- ✅ Covers all energy types & archetypes
- ✅ Optimizes trade-offs (not just mean or worst-case)
- ✅ Validates on realistic field (public suite)
- ✅ Produces actionable decks (top 3 per type, ranked by fitness profile)
- ✅ Discoverable anti-meta strategies (Control beats Alakazam's weakness?)

---

**Next Action:** User decides on Alakazam upload path (A vs B). Parallel: Prep Phase 3a implementation.

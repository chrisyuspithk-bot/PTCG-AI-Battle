# Deck Ranking — 2026-06-21

Comprehensive ranking of all tested decks by best available metric. **Public suite gate is the most reliable filter** (realistic field proof).

---

## Tier 1: Proven Strong (Public Suite >50%)

| Rank | Deck | Brain | Best Metric | Details |
|---:|---|---|---:|---|
| **1** | **Ryotasueyoshi Alakazam best5** | Rule-based (best5) | **57.3%** @ 417g | STRONGEST. Clears vs-1084 (66.7%). Weak: Iono (29.7%), Crustle anti-wall (47.4%) |
| **—** | Alakazam best5 (30g sample) | Rule-based (best5) | 55.3% @ 30g | Same deck, noisier sample (n=30 vs n=417) |

---

## Tier 2: Acceptable Weak (Public Suite 10–20%)

| Rank | Deck | Brain | Best Metric | Details |
|---:|---|---|---:|---|
| **2** | **top_mined_trevenant** | SearchScorer | **15.3%** @ 12g | Leader archetype. Robust pool screen: 0.574 (2nd best). Worst: Kyogre. Not Trevenant-specific logic (deck transfer only). |
| **3** | **a2_kyogre_33_energy** | SearchScorer | **13.2%** @ 12g | Backup / conservative. Robust pool: 0.521. Limited proof (no deep gate). |
| **4** | **robust_deck_search best** | SearchScorer | **12.5%** @ 20g | Optimized for robust (worst-case), but weak on real field. Peaked gen2, never improved. |
| **5** | **Lucario v2 search** | SearchScorer | **11.1%** @ 12g | Leader-suite L1: 69.6% (strong vs known decks), but public is only 11.1%. Large gap = poor transfer. |
| **6** | **gen19_fast_basic** | SearchScorer | **8.3%** @ 12g | Top robust pool screen (0.610), but weakest public gate. Learned policy: 203/240 vs Search 206/240 (SPRT accept_b, learned loses). |

---

## Tier 3: Failed / Not Submission-Ready

| Rank | Deck | Brain | Issue | Details |
|---:|---|---|---|---|
| — | **Lucario RL iter7** | MCTS | 6.9% L1 | Too weak. Severely undertrained (6 rounds/30 min, search_count=10 only). Do not submit. |
| — | **Alakazam Track B 1M** | PPO learned | Failed gate | Kyogre holdout collapsed to 0% by end of training. Gate: 32/110 vs Search 119/240. Do not submit. |
| — | **Lucario RuleCore (deck-tech + Crustle focus)** | Rule-based + deck-tech | 9.5% max | Multiple attempted fixes (search throttling, setup benching, wall routing). Best targeted Crustle: 15%, full public: 9.5%. Not submission-worthy. |
| — | **gen19 spread/control** | SearchScorer | 0% in sampling | Robust fitness 0.753, but public gate not run (lower priority). |

---

## By Category

### Best by Public Suite Gate (Realistic Field)
1. **Alakazam best5** — 57.3% (n=417 games) ← **ONLY ONE CLEARING 50%**
2. Trevenant — 15.3%
3. Kyogre — 13.2%
4. Robust search — 12.5%
5. Lucario search — 11.1%
6. Gen19 fast-basic — 8.3%

### Best by Robust Gauntlet Screening (Mined Field)
1. **top_mined_trevenant** — 0.556 robust, 0.689 mean, 0.250 maximin
2. **gen19_fast_basic** — 0.610 robust, 0.709 mean, 0.333 maximin
3. **robust_deck_search best** — 0.529 robust, 0.670 mean, 0.000 maximin
4. **a2_kyogre** — 0.521 robust, 0.676 mean, 0.000 maximin

### Best by Track B Learned Policy (Policy RL)
1. **gen19_fast_basic** — 203/240 vs Search 206/240, SPRT accept_b (Learned competitive but loses slightly)
2. (No other Track B learned candidates gated successfully)

---

## Key Observations

### Why Alakazam Dominates
- **Sophisticated rule-based logic** beats all novel deck/policy combinations
- **Policy >> deck novelty** — Alakazam's best5 policy is the limiting factor
- All search/RL decks gate 8–15% despite novel deck designs (pilot quality is bottleneck)

### Why Novel Decks Underperform
- **Robust gauntlet ≠ public suite**
  - Gen19 fast-basic: 0.610 robust vs 8.3% public (4.2× gap)
  - Trevenant: 0.556 robust vs 15.3% public (3.6× gap)
- **Transferability problem**
  - Decks optimized for heuristic/search pilots don't transfer to real-world opponents
  - Rule-based Alakazam avoids this (sophisticated logic beats any deck type)

### For Next Phase
- **Path A:** Upload Alakazam best5 (only proven strong deck at 57.3%)
- **Path B:** Fix Alakazam weaknesses (Iono 29.7%, Crustle 47.4%) before re-uploading
- **Do NOT upload:** Gen19, Trevenant, Kyogre, Lucario variants, RL models (all <20% and likely to underperform ladder expectations)

---

## Deck Details for Reference

### Tier 1

**Alakazam best5**
- Location: `dist/candidates/ryotasueyoshi_alakazam_best5.tar.gz`
- Brain: Public rule-based (imported from Kaggle)
- Deck: `deck.csv` bundled with agent
- Gate: 57.3% @ 417g (n=417 per matchup)
- Strengths: Powerful Hand setup, Fezandipiti draw, deck-out safety
- Weaknesses: Iono disruption (29.7%), walls (Crustle 47.4%), no secondary attacker insurance
- Attempted fixes: Deck-out guard relaxation (regressed to 22%), so structural problem

### Tier 2

**top_mined_trevenant**
- Location: `agent_decks/top_mined_trevenant.csv`
- Brain: SearchScorer (not Trevenant-specific)
- Gate: 15.3% public, 0.556 robust gauntlet
- Notes: Mined from ladder; matches leader archetype but SearchScorer is weak pilot

**gen19_fast_basic**
- Location: `agent_decks/deck_rl/gen19_fast_basic.csv`
- Brain: SearchScorer (public) or learned policy (Track B)
- Gate: 8.3% public (SearchScorer), 203/240 Track B learned vs 206/240 Search (SPRT accept_b, loses)
- Notes: Top robust screening pick (0.610) but worst public gate; deck/pilot mismatch

---

**Status:** Tier 1 only ready for upload. All others expected to underperform ladder expectations.

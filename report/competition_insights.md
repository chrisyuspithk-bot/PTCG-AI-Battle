# Competition Insight Base — mined from top public code (2026-06-20)

Source: Kaggle `pokemon-tcg-ai-battle` (Simulation) + Strategy comp code, pulled via CLI to
`data/kaggle_ref/community/` and `data/kaggle_ref/rule_agents/`. This organizes the **best
public insights** and rethinks our approach. We **improve upon** these, we do not copy them.

---

## 1. Score tiers — what each level of play looks like

| Tier | Score | What it is |
|---|---|---|
| Random | ~baseline | legal-random |
| Official rule agents (kiyota) | **~600** | greedy per-deck: lethal detection, prize-trade, weakness×2. The FLOOR. |
| roman Crustle+Lucario v7→v9 | **860–960** | rule core + Crustle-aware + deck tuning |
| kokinn / penguin "Lucario search" | **915** | rule core + light search |
| makthanithin "1084.5" | **1084** | rule core + **opponent-archetype detection + matchup guards** + tuned deck |
| Leaderboard leaders | **1150–1305** | unknown; likely deeper search/MCTS on strong priors + broad meta coverage |

**Our current agents sit BELOW the 600 floor** on ladder (generic heuristic/search ≈ 500–633,
learned ≈ 500). That's the gap to close first.

## 2. The single biggest lever: opponent-archetype detection + matchup switching

The jump from 600 → 1084 is **not** a better core loop — it's the same greedy core PLUS
**reading the opponent and switching plan**. From the 1084 agent (`LucarioPolicy`):

- `_opponent_is_crustle_wall()` → detects Dwebble(344)/Crustle(345). Crustle **prevents damage
  from Pokémon-ex**, hard-walling Mega Lucario ex. Response: **skip attacking Crustle with the ex,
  switch to the non-ex Hariyama line**, prioritize energy onto Hariyama/Makuhita. This one guard
  moved the Crustle matchup **0.47 → 0.77**.
- `_opponent_is_water_deck()` → Kyogre/Snover/Abomasnow. Adjusts Hero Cape targeting + avoids
  overcommitting the ex when behind on prizes.
- opponent has stage2 → Gravity Mountain valuation changes.

**Takeaway for us:** a strong per-deck rule core + opponent detection + a handful of matchup
guards is the proven ~900–1000 path. This is the "opponent-adaptive routing" idea, confirmed by
the top public agent.

## 3. The metagame is Crustle-centric AND fast-moving

From `daily-public-meta-notes`:
- **2026-06-17:** visible top-10 was **10/10 Crustle-style sustain/wall/deck-out**.
- **2026-06-18:** shifted to **Iono lightning tempo 3/10, Psychic control 2/10, Crustle 2/10,
  grass/fire/spread 3/10**. Meta moves day-to-day.
- **Lesson:** do NOT overfit one archetype. Evaluate against **broad families**:
  1. Fast tempo / energy acceleration (Iono, Raging Bolt)
  2. Psychic control (Alakazam)
  3. Sustain / wall / deck-out (Crustle)
  4. Hybrid midrange w/ backup attacker

**Crustle is the pivotal matchup** — it's a wall that beats ex-attackers; most top agents are
explicitly "Crustle-aware / anti-wall." Any Lucario-ex agent that ignores Crustle gets walled.

## 4. Evaluation methodology we're missing

The 1084 agent gates against the **actual public agent suite**, 30–100 games each:
kiyota dragapult/iono/abomasnow, roman crustle_lucario, kokinn lucario-search-915,
penguin public-915, harukiharada crustle, pixiux crustle, biohack crustle, zoli dragapult,
nursrijan lucario, yakitori raging-bolt, pilkwang lucario-v2, kacchan anti-wall.

It reports **mean win-rate across the suite** + **targeted matchup confirmation** (e.g. 100-game
Crustle check). We have these agents downloaded now → we can build the same gate.

**Our gating has been vs random / `pool_*` proxies, which do NOT predict ladder.** Replacing the
gate with "vs the public agent suite" is the highest-value infra change.

## 5. Approaches seen (for our Track choices)
- **Rule + metagame (dominant public approach):** 600→1084. Cheap, robust, no training.
- **Light search ("Lucario search"):** ~915. Search over the rule priors.
- **RL/PPO:** `88% WR Charizard ex PPO` (strategy comp), kiyota MCTS/AZ sample, `tiny RL` guide.
  RL exists but the *top public ladder* agents are refined rule+metagame, not raw RL.

---

## 6. Rethought approach for OUR best scores

**Diagnosis:** we chased RL (PPO→distill) which is below the rule floor, and gated vs proxies that
don't predict ladder. The public evidence says the fast climb is rule-core + opponent detection +
gate-vs-public-field.

**New plan (improve, don't copy):**

1. **Build the public-agent eval gate FIRST.** Wire the downloaded public agents
   (`data/kaggle_ref/community`, `rule_agents`) as opponents in our arena; gate candidates at
   30–100 games each; report suite mean + per-matchup. This is our new source of truth (replaces
   random/`pool_*`). *Nothing ships unless it clears the public field.*

2. **Strong per-deck rule core + opponent detection — our own implementation.** Take the
   *principles* (lethal, prize-trade, weakness, Crustle/water/tempo/psychic detection + matchup
   guards), build them into OUR `OptionScorer` generalized across decks (not a copy of one deck's
   hardcoded policy). Target: clear ~900–1000 on the public gate.

3. **Then exceed them with search.** The leaders (1300) beat the 1084 rule agent — the public
   ceiling. To pass it we add what the public agents lack: **MCTS (engine Search API) using the
   strong rule core as the prior/rollout policy** (rule-guided search > raw AZ from scratch, and >
   rule alone). `az_train.py` already proves MCTS runs at ~15ms/move. Warm-start AZ by imitating
   the rule core, improve via self-play **against the public-agent suite**, gate vs the suite.

4. **Deck:** use the refined meta lists; the 1084's tuned Lucario list (extra Boss's Orders,
   Riolu, Gravity Mountain) outperforms the vanilla official list — worth adopting/tuning per the
   matchup spread, especially the Crustle matchup.

**Build order:** (1) public-agent gate → (2) rule core + opponent detection, gate to ~900+ →
(3) MCTS-on-rule-prior to exceed 1084 → submit only what clears the gate.

---

## 7. Downloaded references
- `data/kaggle_ref/rule_agents/` — 4 official kiyota rule agents (Lucario/Dragapult/Iono/Abomasnow)
- `data/kaggle_ref/community/` — 1084 baseline, roman crustle+lucario 950, kokinn/penguin 915,
  ryotasueyoshi Alakazam (best 5th), dashimaki crustle-beater, kacchan anti-wall, zoli dragapult,
  kojimar matchup-tests, makimakiai meta-notes + tiny-RL, charizard PPO
- `data/kaggle_ref/reinforcement-learning-and-mcts-sample-code.ipynb` — AZ/MCTS sample

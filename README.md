# PTCG AI Battle Challenge — project workspace

Workspace for the Kaggle **[PTCG AI Battle Challenge](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy)**
(Strategy track, ends 2026-09-14) and its sibling **Simulation** ladder
([pokemon-tcg-ai-battle](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle), the live μ
ranking). The project was reset on 2026-06-22 (Session 44) — see `RULINGS.md` for why.

## Read in this order

| # | File | What it is |
|---|------|-----------|
| 1 | **`STATE.md`** | Current state + single next action |
| 2 | **`eval/AGENT_CATALOG_FULL.md`** | All 21 ladder submissions decoded (brain × deck × training) |
| 3 | **`RULINGS.md`** | Mindset + evidence + standing rulings |
| 4 | **`ROADMAP.md`** | Now / next / not doing |
| 5 | **`AGENTS.md`** | Operating contract |

`TASKS.md` = build backlog. No other top-level handoff files (R10).

## The one-paragraph situation

Imperfect-information POMDP on a TrueSkill ladder. After **21 COMPLETE submissions**: only **Dragapult official pilot @ 880.9 μ** clears 800; best **home-grown** is **SearchScorer × Lucario @ 660.5 μ**. Field RL+MCTS v5 **regressed to 580.6 μ** on the same deck. Every Track B / Snorlax-MCTS path ≤585. **Ladder μ sorts; local gates filter.**

See `eval/AGENT_CATALOG_FULL.md` before any train or upload.

## Repository map

```
STATE.md RULINGS.md ARCHITECTURE.md AGENTS.md TASKS.md   # canon
.cursor/SESSION.md                                      # ephemeral session (Cursor hook)
core/        # card/rules/engine/obs model            (scaffold — build first)
field/       # real-field decks + public agents       (scaffold)
episodes/    # Kaggle episode pull/parse/store         (scaffold)
eval/        # the one eval harness + gates            (scaffold)
meta/        # daily meta map                          (scaffold)
discovery/   # scoped deck search                      (scaffold)
agent/       # SHIPPED spine + per-deck agents         (live — do not break)
  lucario_policy.py, lucario_mcts_{runtime,policy}.py, dragapult_agent.py, …
scripts/     # package, gate, train, fetch helpers     (live)
agent_decks/ # real_* + top_mined_* + benchmark/       (live → migrate to field/decks/)
rl_mcts_field/  # local Lucario train outputs (gitignored)
data/        # official rules + card CSVs + engine     (live)
dist/        # packaged submissions                    (live)
tests/       # legality/rules/harness tests            (to populate)
# Reference notebooks at repo root (not under notebooks/):
reinforcement-learning-and-mcts-sample-code.ipynb
a-sample-rule-based-agent-mega-lucario-ex-deck.ipynb
```

## You must provide
- **Kaggle API token** at `.kaggle/` (gitignored) — used to fetch data and pull episodes.
- **A machine with Python ≥3.11** for the engine and the episode pull (this sandbox is 3.10 and has
  no Kaggle egress).

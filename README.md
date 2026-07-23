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

Imperfect-information POMDP on a TrueSkill ladder. After **29 COMPLETE submissions**: best is **Archaludon/Cinderace pure rules agent @ 808.6 μ (v3)**, built from baseline (1196 μ → 808 μ improvement). Current v12 = v3 + Duraludon energy priority boost. **Meta snapshot** confirms Archaludon is the **#1 archetype** (62.2% field WR), with Alakazam/Dunsparce as its only losing matchup (39.1%). Top agents (930-950 μ) use beam search + MCTS. **Ladder μ sorts; local gates filter.**

See `eval/AGENT_CATALOG_FULL.md` before any train or upload.

## Submission history (Archaludon/Cinderace)

| Version | μ Score | Change | Key insight |
|---------|---------|--------|-------------|
| v3 | **808.6** | Baseline (wrong card IDs) | Accidental matchups created beneficial aggressive tilt |
| v7 | 769.4 | Fixed IDs + 6 new matchups | New matchups add ~54 μ over bare fix |
| v8 | 608.1 | v7 - Alakazam override | Removing one override tanked score |
| v9 | 715.5 | v3 + fixed IDs only | Fixing IDs lost ~93 μ! Wrong IDs were accidentally beneficial |
| v10 | 696.0 | v9 + Fire matchup | Worse — Fire override hurt mirror WR |
| v11 | 761.9 | Exact v3 restore | TrueSkill noise ±30 μ (~50 games) |
| **v12** | **pending** | v3 + Duraludon attach +3000 | Match meta's aggro profile (T2.66 first attack) |

## Meta snapshot highlights (July 7, 2026)

| Archetype | Field % | Field WR | Archa WR vs |
|-----------|---------|----------|-------------|
| Alakazam/Dunsparce | 18.96% | 51.3% | **39.1%** ← worst matchup |
| Lucario | 18.78% | 42.4% | 64.4% |
| Hop/Trevenant | 17.52% | 45.5% | 80.6% |
| **Archaludon** | 14.57% | **62.2%** | mirror |
| Starmie | 13.85% | 51.9% | 73.8% |
| Dragapult | 7.31% | 49.1% | 66.2% |

**Top agents use:** beam search + MCTS (cg.api search), 2.6s budget, BEAM_WIDTH=10. Best public: probability v2 @ 933.8 μ (bronze), meta snapshot @ 947.5 μ (silver).

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

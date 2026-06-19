# Track B deck spread — LearnedScorer vs meta pool

Generated: 2026-06-19T17:22:11.089292+00:00
Games per opponent: 12 | Pool opponents: 6

| Rank | Deck | Group | Wins | Rate | Source | Package |
|-----:|------|-------|-----:|-----:|--------|---------|
| 1 | `kyogre` | high_performer | 59/72 | 81.9% | `agent_decks/a2_kyogre_33_energy.csv` | `track_b_learned_kyogre.tar.gz` |
| 2 | `big_basic` | high_performer | 58/72 | 80.6% | `agent_decks/a2_big_basic_29_energy.csv` | `track_b_learned_big_basic.tar.gz` |
| 3 | `starmie` | high_performer | 56/72 | 77.8% | `agent_decks/a3_starmie_spread_33_energy.csv` | `track_b_learned_starmie.tar.gz` |
| 4 | `dragapult` | meta | 48/72 | 66.7% | `agent_decks/pool_dragapult.csv` | `track_b_learned_dragapult.tar.gz` |
| 5 | `crustle` | meta | 45/72 | 62.5% | `agent_decks/pool_crustle.csv` | `track_b_learned_crustle.tar.gz` |
| 6 | `alakazam` | meta | 36/72 | 50.0% | `agent_decks/pool_alakazam_dudunsparce.csv` | `track_b_learned_alakazam.tar.gz` |
| 7 | `greninja` | meta | 36/72 | 50.0% | `agent_decks/pool_greninja.csv` | `track_b_learned_greninja.tar.gz` |
| 8 | `mega_greninja` | meta | 28/72 | 38.9% | `agent_decks/pool_mega_greninja.csv` | `track_b_learned_mega_greninja.tar.gz` |
| 9 | `bellibolt` | meta | 24/71 | 33.8% | `agent_decks/pool_bellibolt.csv` | `track_b_learned_bellibolt.tar.gz` |

## Ladder probe order (diverse archetypes)

Use up to 5 Simulation submits/day. Kyogre heuristic already live (#53854707).
Probe one meta + one high-performer per day; fetch logs after each:

```bash
python scripts/track_ladder.py --fetch-logs
```

## Submit command (user approval required)

```bash
kaggle competitions submit -c pokemon-tcg-ai-battle \
  -f dist/candidates/track_b_learned_<slug>.tar.gz \
  -m "Track B LearnedScorer + <slug> deck probe"
```

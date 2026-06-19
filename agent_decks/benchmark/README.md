# Deck RL benchmark suite

Meta pool decks (`pool_*.csv`) stand in for **Worlds / championship-field**
archetypes until official lists are added. Sources: wmh ladder write-up in
`data/META_NOTES.md` (Dragapult, Crustle, Bellibolt, Alakazam+Dudunsparce, etc.).

## Fitness

`rl/train_deck_campaign.py` uses **weighted win rate** vs this suite as deck
fitness, with a soft **composition penalty** if energy/Pokémon/trainer counts
leave archetype bands (`rl/deck_profiles.json`).

### Suggested composition (from our decks)

| Archetype | Energy | Pokémon | Trainers | Examples |
|-----------|-------:|--------:|---------:|----------|
| **basic_heavy** | 27–37 | 10–18 | 10–18 | Kyogre, Abomasnow pilot, big basic |
| **meta_standard** | 16–24 | 12–20 | 22–30 | dragapult, crustle, bellibolt, alakazam |

Cross-archetype crossover is blocked; mutations rebalance within the parent's band.

## Add real Worlds decks

1. Save 60-card CSV under `agent_decks/benchmark/worlds_<year>_<archetype>.csv`
2. Append to `suite.json` with `"tag": "worlds"` and a weight (1.0–1.5)

Validate with `python scripts/validate_deck.py --deck <path>`.

## Quick eval

```bash
python rl/benchmark.py
python rl/train_deck_campaign.py --phase deck --generations 5 --population 8 --games-eval 4
```

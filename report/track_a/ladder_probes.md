# Track A ladder probes (two submissions)

Generated: 2026-06-19T17:22:20.227404+00:00

Deck grid: SearchScorer vs meta pool @ 12 games/matchup.
Energy grid: `-4,-2,0,2,4` on bases: `agent/deck.csv,agent_decks/a2_kyogre_33_energy.csv,agent_decks/a2_big_basic_29_energy.csv,agent_decks/a4_basic_water_33_energy.csv`

## Probe pair

| Slot | Archive | Deck | Label | Pool win % | Agent | Purpose |
|---|---|---|---|---:|---|---|
| A1 | `dist/candidates/track_a_probe_1.tar.gz` | `agent_decks/track_a_probes/probe_1_a2_kyogre_33_energy_e+2.csv` | a2_kyogre_33_energy_e+2 | 91.7% | SearchScorer | Best Kyogre + SearchScorer (deck-tuned +2 energy) |
| A2 | `dist/candidates/track_a_probe_2.tar.gz` | `agent_decks/track_a_probes/probe_2_deck_e+4.csv` | deck_e+4 | 87.5% | SearchScorer | Second archetype: Abomasnow pilot + SearchScorer (+4 energy) |

## Submit (DO NOT run without explicit user OK)

```
kaggle competitions submit -c pokemon-tcg-ai-battle -f Z:\kaggle\pokemon\dist\candidates\track_a_probe_1.tar.gz -m "Track A probe A1: a2_kyogre_33_energy_e+2 SearchScorer (user approval required)"
```

```
kaggle competitions submit -c pokemon-tcg-ai-battle -f Z:\kaggle\pokemon\dist\candidates\track_a_probe_2.tar.gz -m "Track A probe A2: deck_e+4 SearchScorer (user approval required)"
```

After each submit:
```
python scripts/track_ladder.py --fetch-logs
```

Compare ladder μ after ~40 min matchmaking (600 = validation baseline only).

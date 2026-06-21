# Ryotasueyoshi Alakazam Baseline Import

Date: 2026-06-20

Source kernel:
`https://www.kaggle.com/code/ryotasueyoshi/rule-based-not-psychic-alakazam-best-5th`

Local pull:
`notebooks/ryotasueyoshi_rule_based_alakazam_best5/`

Built archive:
`dist/candidates/ryotasueyoshi_alakazam_best5.tar.gz`

Importer:
`scripts/import_notebook_candidate.py`

## What Was Imported

The notebook contains `%%writefile deck.csv` and `%%writefile main.py` cells.
The importer extracts those cells, copies the local `cg/` simulator package,
and builds a Kaggle-shaped archive.

The notebook `main.py` originally loaded `deck.csv` from the current working
directory or `/kaggle_simulations/agent/deck.csv`. The importer normalizes this
to also check `deck.csv` beside `__file__`, so the archive works in the local
import-based verifier while preserving Kaggle compatibility.

## Baseline Deck IDs

```text
741 x4  Abra
742 x4  Kadabra
743 x3  Alakazam
305 x3  Dunsparce
66  x2  Dudunsparce
140 x1  Fezandipiti ex
142 x1  Genesect
858 x1  Psyduck
343 x1  Shaymin
1079 x3 Rare Candy
1081 x3 Enhanced Hammer
1086 x4 Buddy-Buddy Poffin
1097 x1 Night Stretcher
1129 x1 Sacred Ash
1152 x4 Poke Pad
1156 x3 Lucky Helmet
1182 x2 Boss's Orders
1225 x4 Hilda
1231 x4 Dawn
1264 x4 Battle Cage
5   x2 Basic Psychic Energy
19  x4 Telepath Psychic Energy
13  x1 Enriching Energy
```

## Verification

Archive verification vs legal random:

```text
dist/candidates/ryotasueyoshi_alakazam_best5.tar.gz:
15/20 wins, 75.00% decided; random 5, draws 0, unfinished 0, avg_steps 79.5
```

Lightweight public-field gate:

```text
games: 6 per opponent, 12 opponents
suite mean: 56.3% (40/71 decided)
per-matchup mean: 56.4%
```

Worst matchups:

```text
16.7%  simple-baseline-matchup-tests
33.3%  a-sample-rule-based-agent-dragapult-ex-deck
33.3%  crustle-aware-mega-lucario-ex-anti-wall
```

## Recommendation

Use this as the rule-based Alakazam comparison baseline before spending a full
1M-step Track B run. The useful features to transfer or distill are:

- Powerful Hand damage planning from hand-size growth.
- Deck-out safety based on deck count vs remaining prizes.
- Conditional Fezandipiti ex, Dudunsparce, and draw use only when it changes a KO/setup line.
- Matchup tech deployment for Psyduck, Shaymin, Battle Cage, Enhanced Hammer, and Lucky Helmet.

Next concrete action: run a stronger 30-game public gate for this archive after
the current background validation chain finishes, then compare against
`track_b_learned_alakazam` and the planned per-deck Alakazam Track B training.

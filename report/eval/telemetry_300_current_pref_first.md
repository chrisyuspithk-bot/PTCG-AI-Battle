# Game Telemetry (300 games per ordered matchup)

One row in the CSV is one agent perspective for one game.

## Results By Agent

| Agent | Games | Wins | Losses | Draws | Win % | Avg turns | Avg missed attach turns | Avg first evolve turn |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| current | 600 | 578 | 22 | 0 | 96.3 | 5.2 | 0.00 | 3.8 |
| random | 600 | 22 | 578 | 0 | 3.7 | 5.2 | 0.47 | 4.6 |

## Results By First/Second

| Agent | Order | Games | Wins | Losses | Win % | Avg turns | Avg missed attach turns |
|---|---|---:|---:|---:|---:|---:|---:|
| current | first | 460 | 448 | 12 | 97.4 | 4.9 | 0.00 |
| current | second | 140 | 130 | 10 | 92.9 | 6.3 | 0.00 |
| random | first | 140 | 10 | 130 | 7.1 | 6.3 | 0.80 |
| random | second | 460 | 12 | 448 | 2.6 | 4.9 | 0.37 |

## Loss Reasons

| Agent | Reason | Losses | Avg turns | Avg deck left | Avg opp prizes left |
|---|---|---:|---:|---:|---:|
| current | no_active | 22 | 8.8 | 41.4 | 4.0 |
| random | no_active | 577 | 5.0 | 43.8 | 4.5 |
| random | prize | 1 | 19.0 | 36.0 | 0.0 |

## Common Decision Contexts In Losses

| Agent | Context counts |
|---|---|
| current | MAIN:243;DISCARD_ENERGY:40;TO_HAND:27;SETUP_ACTIVE_POKEMON:22;ATTACH_TO:18;ATTACH_FROM:18;TO_ACTIVE:13;IS_FIRST:8;SETUP_BENCH_POKEMON:8;DRAW_COUNT:7 |
| random | MAIN:3049;SETUP_ACTIVE_POKEMON:578;TO_HAND:301;IS_FIRST:286;TO_ACTIVE:199;DRAW_COUNT:184;SETUP_BENCH_POKEMON:156;ATTACH_TO:120;DISCARD_ENERGY:43;SWITCH:4 |

## Active Attackers

| Agent | Attack counts | Last attacker counts |
|---|---|---|
| current | 721:821;723:756;722:449 | 723:435;721:152;722:13 |
| random | 722:385;721:309;723:109 | 722:187;721:130;723:40 |

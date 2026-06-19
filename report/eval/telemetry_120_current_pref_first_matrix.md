# Game Telemetry (120 games per ordered matchup)

One row in the CSV is one agent perspective for one game.

## Results By Agent

| Agent | Games | Wins | Losses | Draws | Win % | Avg turns | Avg missed attach turns | Avg first evolve turn |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| current | 480 | 387 | 93 | 0 | 80.6 | 5.6 | 0.00 | 3.6 |
| random | 480 | 20 | 460 | 0 | 4.2 | 5.6 | 0.61 | 4.4 |
| safety | 480 | 313 | 167 | 0 | 65.2 | 5.9 | 0.00 | 4.4 |

## Results By First/Second

| Agent | Order | Games | Wins | Losses | Win % | Avg turns | Avg missed attach turns |
|---|---|---:|---:|---:|---:|---:|---:|
| current | first | 416 | 324 | 92 | 77.9 | 5.5 | 0.00 |
| current | second | 64 | 63 | 1 | 98.4 | 6.3 | 0.00 |
| random | first | 248 | 13 | 235 | 5.2 | 6.1 | 0.78 |
| random | second | 232 | 7 | 225 | 3.0 | 5.0 | 0.42 |
| safety | first | 56 | 53 | 3 | 94.6 | 4.9 | 0.00 |
| safety | second | 424 | 260 | 164 | 61.3 | 6.0 | 0.00 |

## Loss Reasons

| Agent | Reason | Losses | Avg turns | Avg deck left | Avg opp prizes left |
|---|---|---:|---:|---:|---:|
| current | no_active | 79 | 6.5 | 40.9 | 3.9 |
| current | prize | 14 | 13.4 | 27.3 | 0.0 |
| random | no_active | 449 | 5.1 | 43.7 | 4.6 |
| random | prize | 11 | 16.0 | 28.5 | 0.0 |
| safety | no_active | 160 | 5.1 | 41.5 | 4.1 |
| safety | prize | 7 | 14.6 | 26.9 | 0.0 |

## Common Decision Contexts In Losses

| Agent | Context counts |
|---|---|
| current | MAIN:1031;TO_HAND:159;SETUP_ACTIVE_POKEMON:93;TO_ACTIVE:65;ATTACH_TO:62;ATTACH_FROM:62;DISCARD_ENERGY:52;IS_FIRST:43;DRAW_COUNT:26;SETUP_BENCH_POKEMON:16 |
| random | MAIN:2675;SETUP_ACTIVE_POKEMON:460;TO_HAND:237;IS_FIRST:230;TO_ACTIVE:155;DRAW_COUNT:141;SETUP_BENCH_POKEMON:126;ATTACH_TO:119;DISCARD_ENERGY:30;SWITCH:3 |
| safety | MAIN:1242;TO_HAND:213;SETUP_ACTIVE_POKEMON:167;ATTACH_TO:96;ATTACH_FROM:92;TO_ACTIVE:91;IS_FIRST:81;DISCARD_ENERGY:48;SETUP_BENCH_POKEMON:47;DRAW_COUNT:44 |

## Active Attackers

| Agent | Attack counts | Last attacker counts |
|---|---|---|
| current | 723:802;721:577;722:292 | 723:338;721:113;722:29 |
| random | 721:282;722:273;723:102 | 722:145;721:106;723:42 |
| safety | 721:703;722:688;723:632 | 723:276;721:138;722:66 |

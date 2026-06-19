# Simulation Submission Candidates

Date: 2026-06-19

No Kaggle submission has been made. These archives are local dry-run packages
under `dist/candidates/`. Re-open the official Kaggle pages in a browser and get
explicit user confirmation before uploading any slot.

## Candidate Set

| Slot | Archive | Agent module | Deck | Purpose | Current local evidence |
|---|---|---|---|---|---|
| A0 | `dist/candidates/a0_safety.tar.gz` | `agent_snapshots.v2_safety` | `agent/deck.csv` | Frozen no-regression baseline | Historical best 88.7% over 300 vs legal random before A1/A2 work |
| A1 | `dist/candidates/a1_current_963.tar.gz` | `agent.agent` | `agent/deck.csv` | Best current Abomasnow pilot | `matrix_300_current_pref_first`: 578/600 = 96.3% vs legal random; `matrix_120_current_pref_first_matrix`: beats safety 152/240 |
| A2 | `dist/candidates/a2_kyogre.tar.gz` | `agent.agent` | `agent_decks/a2_kyogre_33_energy.csv` | Reduced Energy plus more Kyogre backups | 561/600 = 93.5% vs legal random in overwritten `matrix_300` run; not current best |
| A3 | `dist/candidates/a3_starmie.tar.gz` | `agent.agent` | `agent_decks/a3_starmie_spread_33_energy.csv` | Mega Starmie spread pressure | Small 44-game ordered row hit 95.5% vs random, but 60-game rerun fell to 91.7%; loses to safety |
| A4 | `dist/candidates/a4_big_basic.tar.gz` | `agent.agent` | `agent_decks/a2_big_basic_29_energy.csv` | Black Kyurem ex robustness probe | 120-game quick gate 233/240 = 97.1%, but 300-game rerun fell to 565/600 = 94.2% |

## Submission Order Recommendation

1. Submit A1 first if we decide to spend a Simulation slot today.
2. Submit A0 only if we want a conservative baseline ladder anchor.
3. Submit A4 as the most strategically distinct robustness probe.
4. Hold A2/A3 unless we want diversity over current local strength.

## Remaining Validation Gap

The local 95% target is achieved for A1 against legal random. This is not proof
of Kaggle ladder performance. Actual ladder validation requires a user-approved
upload and recording the submission ID/score.

"""Mine real 60-card decklists from Kaggle episode replays.

Each episode JSON embeds both players' full decks at
steps[0][p].visualize[0].action[p], plus final rewards (win=+1/loss=-1) and
team names. This extracts decklists, tags them by archetype marker cards, and
writes the most common WINNING list per target archetype as agent_decks CSVs
(one card ID per line — the format _load_deck expects).

    python scripts/mine_episode_decks.py --episodes data/kaggle_ref/episodes \
        --out-dir agent_decks --report report/real_decks_mined.md
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Archetype marker card IDs (presence => that archetype). Iono is a supporter,
# matched by name. The 4 named competition decks are the priority targets.
MARKERS = {
    "dragapult_ex": 121,
    "mega_lucario_ex": 678,
    "mega_abomasnow_ex": 723,
}
TARGETS = ["iono", "dragapult_ex", "mega_abomasnow_ex", "mega_lucario_ex"]


def _card_names() -> dict[int, str]:
    out: dict[int, str] = {}
    p = ROOT / "data" / "EN_Card_Data.csv"
    with open(p, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[int(r["Card ID"])] = r["Card Name"]
    return out


def _decks_from_episode(path: Path):
    """Yield (deck_card_ids, reward, team_name) for both players."""
    d = json.loads(path.read_text(encoding="utf-8"))
    try:
        actions = d["steps"][0][0]["visualize"][0]["action"]
    except (KeyError, IndexError, TypeError):
        return
    rewards = d.get("rewards") or [None, None]
    names = (d.get("info") or {}).get("TeamNames") or [None, None]
    for i, deck in enumerate(actions):
        if isinstance(deck, list) and len(deck) == 60:
            yield [int(c) for c in deck], rewards[i] if i < len(rewards) else None, \
                names[i] if i < len(names) else None


def _archetypes(deck: list[int], cardname: dict[int, str]) -> list[str]:
    ids = set(deck)
    tags = [a for a, cid in MARKERS.items() if cid in ids]
    if any("Iono" in cardname.get(c, "") for c in ids):
        tags.append("iono")
    return tags


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", default=str(ROOT / "data" / "kaggle_ref" / "episodes"))
    ap.add_argument("--out-dir", default=str(ROOT / "agent_decks"))
    ap.add_argument("--report", default=str(ROOT / "report" / "real_decks_mined.md"))
    ap.add_argument("--prefix", default="real_", help="Output CSV filename prefix")
    args = ap.parse_args(argv)

    cardname = _card_names()
    files = sorted(Path(args.episodes).glob("*.json"))
    # winners[arch] = Counter of exact decklists (as tuple) seen in WINS
    winners: dict[str, Counter] = defaultdict(Counter)
    allseen: dict[str, Counter] = defaultdict(Counter)
    n_decks = 0
    arch_counts: Counter = Counter()
    for fp in files:
        for deck, reward, _name in _decks_from_episode(fp):
            n_decks += 1
            sig = tuple(sorted(deck))
            for a in _archetypes(deck, cardname):
                arch_counts[a] += 1
                allseen[a][sig] += 1
                if reward == 1:
                    winners[a][sig] += 1

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Mined real decklists from episode replays", "",
        f"Episodes scanned: {len(files)}  |  decks parsed: {n_decks}", "",
        "| Archetype | seen | wins | written |", "|---|---|---|---|",
    ]
    written: dict[str, str] = {}
    for arch in TARGETS:
        pool = winners[arch] or allseen[arch]
        note = ""
        if pool:
            sig, _cnt = pool.most_common(1)[0]
            csv_path = out_dir / f"{args.prefix}{arch}.csv"
            csv_path.write_text("\n".join(str(c) for c in sig) + "\n", encoding="utf-8")
            written[arch] = csv_path.name
            note = csv_path.name
        lines.append(f"| {arch} | {arch_counts[arch]} | {sum(winners[arch].values())} | {note or 'NOT FOUND'} |")

    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {len(written)}/{len(TARGETS)} target decks to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

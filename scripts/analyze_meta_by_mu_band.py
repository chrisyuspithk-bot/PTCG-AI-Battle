#!/usr/bin/env python3
"""Analyze field meta stratified by ladder μ band.

Uses:
  - report/replays/manifest.csv  — episode metadata (avg_score ≈ mean μ of both agents)
  - report/replays/*.json        — replay files (deck lists + outcomes)
  - report/ladder_history.csv      — our submission μ over time
  - report/leaderboard_snap_*.csv  — current leaderboard (optional)

Outputs:
  - report/meta/deck_by_mu_band_<date>.md
  - report/meta/deck_by_mu_band_<date>.json

Usage:
  python scripts/analyze_meta_by_mu_band.py
  python scripts/analyze_meta_by_mu_band.py --download-per-band 8
  python scripts/analyze_meta_by_mu_band.py --replays report/replays --sample 500
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.mine_episode_replays import _archetype, _card_names, _initial_decks, _rewards, _winner  # noqa: E402

MANIFEST_PATH = ROOT / "report" / "replays" / "manifest.csv"
META_DIR = ROOT / "report" / "meta"
LADDER_HISTORY = ROOT / "report" / "ladder_history.csv"
OUR_SUBMISSION_LOG = ROOT / "report" / "submission_log.csv"

# Match tier bands by average episode μ (both agents).
MU_BANDS: list[tuple[str, float, float]] = [
    ("elite_1200+", 1200.0, 99999.0),
    ("high_1000_1199", 1000.0, 1199.99),
    ("mid_800_999", 800.0, 999.99),
    ("rising_600_799", 600.0, 799.99),
    ("floor_below_600", 0.0, 599.99),
]


def band_for_avg_mu(avg_mu: float) -> str:
    for name, lo, hi in MU_BANDS:
        if lo <= avg_mu <= hi:
            return name
    return "unknown"


def load_manifest(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("episode_id"):
                rows.append(row)
    return rows


def manifest_band_stats(manifest: list[dict[str, str]]) -> dict[str, dict]:
    """Episode counts and μ stats per band (no deck data)."""
    stats: dict[str, dict] = {name: {"episodes": 0, "avg_mu_sum": 0.0, "min_mu_sum": 0.0} for name, _, _ in MU_BANDS}
    for row in manifest:
        try:
            avg_mu = float(row["avg_score"])
            min_mu = float(row.get("min_score") or avg_mu)
        except (KeyError, ValueError, TypeError):
            continue
        band = band_for_avg_mu(avg_mu)
        if band not in stats:
            continue
        s = stats[band]
        s["episodes"] += 1
        s["avg_mu_sum"] += avg_mu
        s["min_mu_sum"] += min_mu
    for s in stats.values():
        n = s["episodes"]
        if n:
            s["mean_avg_mu"] = s["avg_mu_sum"] / n
            s["mean_min_mu"] = s["min_mu_sum"] / n
        else:
            s["mean_avg_mu"] = 0.0
            s["mean_min_mu"] = 0.0
    return stats


def pick_episode_ids_per_band(
    manifest: list[dict[str, str]],
    per_band: int,
    *,
    seed: int = 42,
) -> dict[str, list[str]]:
    by_band: dict[str, list[str]] = defaultdict(list)
    for row in manifest:
        try:
            avg_mu = float(row["avg_score"])
        except (KeyError, ValueError, TypeError):
            continue
        band = band_for_avg_mu(avg_mu)
        by_band[band].append(row["episode_id"])

    rng = random.Random(seed)
    picked: dict[str, list[str]] = {}
    for name, _, _ in MU_BANDS:
        pool = by_band.get(name, [])
        if not pool:
            picked[name] = []
            continue
        k = min(per_band, len(pool))
        picked[name] = rng.sample(pool, k)
    return picked


def download_replay(episode_id: str, dest_dir: Path) -> bool:
    dest_dir.mkdir(parents=True, exist_ok=True)
    candidates = [
        dest_dir / f"{episode_id}.json",
        dest_dir / f"episode-{episode_id}-replay.json",
    ]
    for dest in candidates:
        if dest.exists() and dest.stat().st_size > 1000:
            return True
    cmd = ["kaggle", "competitions", "replay", episode_id, "-p", str(dest_dir), "-q"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=False)
        if proc.returncode != 0:
            return False
        for dest in candidates:
            if dest.exists() and dest.stat().st_size > 1000:
                # Normalize to {episode_id}.json for downstream tools.
                norm = dest_dir / f"{episode_id}.json"
                if dest != norm and not norm.exists():
                    dest.rename(norm)
                return True
        return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def parse_replay_archetypes(path: Path, names: dict[int, str]) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    rewards = _rewards(data)
    winner = _winner(rewards)
    if winner is None:
        return None
    decks = _initial_decks(data)
    if len(decks) < 2:
        return None
    archs = []
    for i, deck in enumerate(decks[:2]):
        archs.append(_archetype(deck, names) if deck else "unknown")
    loser = 1 - winner
    return {
        "episode_id": path.stem,
        "winner_arch": archs[winner],
        "loser_arch": archs[loser],
        "arch_a": archs[0],
        "arch_b": archs[1],
        "winner": winner,
    }


@dataclass
class BandDeckStats:
    band: str
    games: int = 0
    arch_appearances: Counter = field(default_factory=Counter)
    arch_wins: Counter = field(default_factory=Counter)
    matchups: dict[tuple[str, str], list[int]] = field(default_factory=lambda: defaultdict(lambda: [0, 0]))


def analyze_replays(
    replay_dir: Path,
    manifest: list[dict[str, str]],
    *,
    episode_ids: set[str] | None = None,
    include_unmanifested: bool = True,
) -> tuple[dict[str, BandDeckStats], int, dict[str, BandDeckStats]]:
    """Stratify parsed replays by manifest avg_score band."""
    mu_by_ep = {}
    for row in manifest:
        try:
            mu_by_ep[row["episode_id"]] = float(row["avg_score"])
        except (KeyError, ValueError, TypeError):
            pass

    names = _card_names()
    band_stats = {name: BandDeckStats(band=name) for name, _, _ in MU_BANDS}
    unbanded = BandDeckStats(band="unmanifested_recent")
    parsed = 0

    def episode_id_from_path(path: Path) -> str:
        stem = path.stem
        if stem.startswith("episode-") and stem.endswith("-replay"):
            return stem[len("episode-"):-len("-replay")]
        return stem

    for path in sorted(replay_dir.glob("*.json")):
        ep_id = episode_id_from_path(path)
        if episode_ids and ep_id not in episode_ids:
            continue
        avg_mu = mu_by_ep.get(ep_id)
        if avg_mu is None:
            if not include_unmanifested:
                continue
            target = unbanded
        else:
            band = band_for_avg_mu(avg_mu)
            if band not in band_stats:
                continue
            target = band_stats[band]

        row = parse_replay_archetypes(path, names)
        if row is None:
            continue
        parsed += 1
        bs = target
        bs.games += 1
        bs.arch_appearances[row["arch_a"]] += 1
        bs.arch_appearances[row["arch_b"]] += 1
        bs.arch_wins[row["winner_arch"]] += 1
        a, b = sorted((row["arch_a"], row["arch_b"]))
        if a != b:
            key = (a, b)
            bs.matchups[key][1] += 1
            if row["winner_arch"] == a:
                bs.matchups[key][0] += 1

    return band_stats, parsed, {"unmanifested_recent": unbanded}


def load_our_submissions() -> list[dict[str, str]]:
    if not OUR_SUBMISSION_LOG.exists():
        return []
    with OUR_SUBMISSION_LOG.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load_ladder_peaks() -> dict[str, float]:
    """Best publicScore per ref from ladder history."""
    peaks: dict[str, float] = {}
    if not LADDER_HISTORY.exists():
        return peaks
    with LADDER_HISTORY.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            ref = (row.get("ref") or "").strip()
            score = row.get("publicScore", "")
            if not ref or not score:
                continue
            try:
                mu = float(score)
            except ValueError:
                continue
            peaks[ref] = max(peaks.get(ref, 0.0), mu)
    return peaks


def load_leaderboard_snapshot() -> list[dict[str, str]]:
    snaps = sorted(ROOT.glob("report/leaderboard_snap_*.csv"), reverse=True)
    if not snaps:
        return []
    rows = []
    with snaps[0].open(encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh if ln.strip() and not ln.startswith("Next Page")]
        reader = csv.DictReader(lines)
        for row in reader:
            if row.get("teamId") or row.get("score"):
                rows.append(row)
    return rows


def infer_deck_from_name(name: str) -> str:
    n = name.lower()
    for key, deck in [
        ("lucario", "lucario"), ("dragapult", "dragapult"), ("alakazam", "alakazam"),
        ("kyogre", "kyogre"), ("bellibolt", "bellibolt"), ("trevenant", "trevenant"),
        ("crustle", "crustle"), ("abomasnow", "abomasnow"), ("iono", "iono"),
        ("greninja", "greninja"), ("boss", "mixed"), ("mega", "mixed"),
    ]:
        if key in n:
            return deck
    return "unknown"


def leaderboard_band_summary(lb: list[dict[str, str]]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {name: [] for name, _, _ in MU_BANDS}
    for row in lb:
        try:
            mu = float(row.get("score") or row.get("publicScore") or 0)
        except ValueError:
            continue
        band = band_for_avg_mu(mu)
        if band in out:
            out[band].append({
                "team": row.get("teamName", ""),
                "mu": mu,
                "inferred_deck": infer_deck_from_name(row.get("teamName", "")),
                "date": row.get("submissionDate", ""),
            })
    return out


def write_report(
    *,
    manifest_stats: dict[str, dict],
    band_deck: dict[str, BandDeckStats],
    extra_bands: dict[str, BandDeckStats],
    parsed_count: int,
    manifest_count: int,
    lb_bands: dict[str, list[dict]],
    our_subs: list[dict[str, str]],
    ladder_peaks: dict[str, float],
    download_note: str,
) -> tuple[Path, Path]:
    META_DIR.mkdir(parents=True, exist_ok=True)
    day = date.today().isoformat()
    md_path = META_DIR / f"deck_by_mu_band_{day}.md"
    json_path = META_DIR / f"deck_by_mu_band_{day}.json"

    band_names = {name for name, _, _ in MU_BANDS}
    total_eps = sum(s["episodes"] for s in manifest_stats.values())
    lines = [
        f"# Field meta by μ band — {day}",
        "",
        "**Purpose:** Stratify ladder episode volume and (where replays exist) deck archetype",
        "performance by match skill tier. Informs R3 field-mixture weighting after R2 levers.",
        "",
        f"- Manifest episodes: **{manifest_count}**",
        f"- Replays parsed for decks: **{parsed_count}**",
        f"- {download_note}",
        "",
        "## μ band definitions (by episode `avg_score`)",
        "",
        "| Band | μ range | Manifest episodes | % of field sample | Mean avg μ |",
        "|------|---------|-------------------:|------------------:|-----------:|",
    ]
    for name, lo, hi in MU_BANDS:
        s = manifest_stats.get(name, {})
        n = s.get("episodes", 0)
        pct = 100.0 * n / total_eps if total_eps else 0
        lines.append(
            f"| {name} | {lo:.0f}–{hi:.0f} | {n} | {pct:.1f}% | {s.get('mean_avg_mu', 0):.1f} |"
        )

    lines.extend([
        "",
        "## Interpretation (manifest-only)",
        "",
        "- `avg_score` in the episode manifest is the mean μ of both agents at match time.",
        "- High-band volume shows where the ladder spends matchmaking effort.",
        "- Deck archetypes require replay JSON (60-card lists in step 0).",
        "",
    ])

    if parsed_count > 0:
        lines.append("## Deck archetype by μ band (from parsed replays)")
        lines.append("")
        all_bands = list(band_deck.items()) + list(extra_bands.items())
        for name, bs in all_bands:
            if bs.games == 0:
                continue
            label = name if name in band_names else f"{name} (no manifest μ — recent pull)"
            lines.append(f"### {label} (n={bs.games} parsed games)")
            lines.append("")
            lines.append("| Archetype | Seat appearances | Wins |")
            lines.append("|-----------|-----------------:|-----:|")
            for arch, apps in bs.arch_appearances.most_common():
                wins = bs.arch_wins.get(arch, 0)
                lines.append(f"| {arch} | {apps} | {wins} |")
            if bs.matchups:
                lines.append("")
                lines.append("**Head-to-head (alphabetical first archetype wins):**")
                lines.append("")
                for (a, b), (aw, tot) in sorted(bs.matchups.items(), key=lambda x: -x[1][1])[:8]:
                    pct = 100.0 * aw / tot if tot else 0
                    lines.append(f"- {a} vs {b}: {aw}/{tot} ({pct:.0f}% first-arch wins)")
            lines.append("")

    if any(lb_bands.values()):
        lines.extend([
            "## Current leaderboard by μ band (team names; deck inferred from name)",
            "",
        ])
        for name, _, _ in MU_BANDS:
            teams = lb_bands.get(name, [])
            if not teams:
                continue
            lines.append(f"### {name} ({len(teams)} teams)")
            lines.append("")
            lines.append("| μ | Inferred deck | Team |")
            lines.append("|--:|---------------|------|")
            for t in sorted(teams, key=lambda x: -x["mu"])[:15]:
                lines.append(f"| {t['mu']:.1f} | {t['inferred_deck']} | {t['team'][:50]} |")
            lines.append("")

    if our_subs:
        lines.extend([
            "## Our submissions (measured μ)",
            "",
            "| Ref | Deck | Scorer | Peak μ | Local gate |",
            "|-----|------|--------|-------:|------------|",
        ])
        for row in our_subs:
            ref = row.get("ref", "")
            peak = ladder_peaks.get(ref, float(row.get("mu_24h") or row.get("mu_initial") or 0))
            lines.append(
                f"| {ref} | {row.get('deck', '')} | {row.get('scorer', '')} | {peak:.1f} | {row.get('gate_l1_pct', '')} |"
            )
        lines.append("")

    lines.extend([
        "## How to refresh",
        "",
        "```powershell",
        "python scripts/analyze_meta_by_mu_band.py --download-per-band 10",
        "python scripts/update_from_kaggle.py",
        "```",
        "",
        "See also: `report/RESEARCH_AND_DECISION_BRIEF.md`",
    ])

    md_path.write_text("\n".join(lines), encoding="utf-8")

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest_episodes": manifest_count,
        "parsed_replays": parsed_count,
        "manifest_band_stats": manifest_stats,
        "deck_by_band": {
            name: {
                "games": bs.games,
                "arch_appearances": dict(bs.arch_appearances),
                "arch_wins": dict(bs.arch_wins),
            }
            for name, bs in {**band_deck, **extra_bands}.items()
        },
        "leaderboard_bands": lb_bands,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return md_path, json_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default=str(MANIFEST_PATH))
    ap.add_argument("--replays", default=str(ROOT / "report" / "replays"))
    ap.add_argument("--download-per-band", type=int, default=0, help="Download N replays per μ band")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args(argv)

    manifest = load_manifest(Path(args.manifest))
    if not manifest:
        print(f"No manifest at {args.manifest}")
        return 1

    manifest_stats = manifest_band_stats(manifest)
    replay_dir = Path(args.replays)
    download_note = "No new downloads."

    if args.download_per_band > 0:
        picked = pick_episode_ids_per_band(manifest, args.download_per_band, seed=args.seed)
        ok = fail = 0
        for band, ids in picked.items():
            for ep_id in ids:
                if download_replay(ep_id, replay_dir):
                    ok += 1
                else:
                    fail += 1
        download_note = f"Downloaded {ok} replays ({fail} failed) at {args.download_per_band}/band."

    band_deck, parsed, extra = analyze_replays(replay_dir, manifest)
    lb = load_leaderboard_snapshot()
    lb_bands = leaderboard_band_summary(lb)
    our_subs = load_our_submissions()
    peaks = load_ladder_peaks()

    md_path, json_path = write_report(
        manifest_stats=manifest_stats,
        band_deck=band_deck,
        extra_bands=extra,
        parsed_count=parsed,
        manifest_count=len(manifest),
        lb_bands=lb_bands,
        our_subs=our_subs,
        ladder_peaks=peaks,
        download_note=download_note,
    )

    print(f"Manifest: {len(manifest)} episodes")
    print(f"Parsed replays with deck data: {parsed}")
    print(f"Report: {md_path}")
    print(f"JSON: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Gate Kaggle uploads — R12: no duplicate brain×deck; require iteration hypothesis.

Run before every upload (or after package dry-run):

  # After packaging (manifest exists):
  python scripts/check_upload_eligible.py --manifest dist/candidates/<name>.manifest.json \\
    --change "LucarioScorer: fix bench guard vs Dragapult" --local-gate 58.0

  # Before packaging (brain + deck only):
  python scripts/check_upload_eligible.py --brain LucarioScorer \\
    --deck agent_decks/real_mega_lucario_ex.csv \\
    --change "LucarioScorer: fix X vs ref 53886522" --local-gate 58.0

  python scripts/check_upload_eligible.py --suggest

Exit 0 = eligible (prints checklist). Exit 1 = blocked (prints why + what to do instead).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LADDER_LOG = ROOT / "eval" / "ladder_log.csv"
FAMILIES_PATH = ROOT / "data" / "upload_brain_families.json"
CANDIDATES_DIR = ROOT / "dist" / "candidates"
CATALOG = ROOT / "eval" / "AGENT_CATALOG_FULL.md"

# Rows we know are policy-equivalent — port/repackage does not count as iteration.
POLICY_EQUIVALENT = [
    {
        "name": "ryotasueyoshi_alakazam_best5",
        "ladder_ref": "53913404",
        "ladder_mu": 659.0,
        "brain_family": "alakazam_imported",
        "note": "Notebook best5 rules. Repo port (S50) is same policy — dry-run only.",
    },
    {
        "name": "dragapult_ex_sample",
        "ladder_ref": "53989933",
        "ladder_mu": 880.9,
        "brain_family": "dragapult_crispin",
        "note": "v3 + R7 bench guard. Re-upload only for final lock-in or material lever change.",
    },
]

# Minimum full-suite local WR (n≥30) before a *new* ladder upload is worth a slot.
MIN_LOCAL_GATE_WR_PCT = 55.0

# Same deck — SearchScorer is the home-grown bar to beat on ladder.
SEARCH_LUCARIO_BENCHMARK = {
    "deck_stem": "real_mega_lucario_ex",
    "brain_family": "search",
    "ladder_ref": "53869254",
    "ladder_mu": 660.5,
}

SUGGESTED_NEXT = [
    {
        "id": "B3",
        "brain": "LucarioScorer",
        "deck": "agent_decks/real_mega_lucario_ex.csv",
        "why": "Gated 39.3% @ n=30 — do NOT upload. Iterate SearchScorer (660.5 μ bar) instead.",
        "local_gate": "DONE — eval/lucario_scorer_baseline_session50.md",
        "beat_row": "53886522 (535.6 μ) and ideally 53869254 (660.5 μ)",
    },
    {
        "id": "B5",
        "brain": "SearchScorer",
        "deck": "agent_decks/real_mega_lucario_ex.csv",
        "why": "Best home-grown 660.5 — iterate one targeted fix at a time.",
        "local_gate": "python scripts/gate_search.py --games 30 --suite full --report",
        "beat_row": "53869254 (660.5 μ)",
    },
    {
        "id": "B2",
        "brain": "alakazam_agent + levers",
        "deck": "agent_decks/ryotasueyoshi_alakazam_best5.csv",
        "why": "659 μ exists (53913404). Upload only after local gate beats 62% port baseline.",
        "local_gate": "python scripts/gate_alakazam.py --games 30 --suite full --report",
        "beat_row": "53913404 (659.0 μ) — needs material lever change, not re-port",
    },
    {
        "id": "B6",
        "brain": "SearchScorer",
        "deck": "agent_decks/dragapult_ex_sample.csv",
        "why": "Search on Dragapult deck never on ladder (Dragapult rules own 880.9).",
        "local_gate": "gate vs full suite after wiring",
        "beat_row": "new row — exploratory",
    },
]


def _stem(path: str) -> str:
    return Path(path.replace("\\", "/")).name.replace(".csv", "")


def _load_families() -> dict[str, list[str]]:
    if not FAMILIES_PATH.exists():
        return {}
    data = json.loads(FAMILIES_PATH.read_text(encoding="utf-8"))
    return {k: [x.lower() for x in v] for k, v in data.items()}


def brain_family(brain: str, families: dict[str, list[str]]) -> str:
    b = brain.lower().strip()
    padded = f"_{b}_"
    best: tuple[int, str] | None = None
    for fam, aliases in families.items():
        for a in aliases:
            a = a.lower()
            if b == a:
                return fam
            if b.startswith(a + "_") or b.endswith("_" + a) or f"_{a}_" in padded:
                # prefer longest alias match (more specific family)
                if best is None or len(a) > best[0]:
                    best = (len(a), fam)
    return best[1] if best else b


def _load_ladder() -> list[dict[str, str]]:
    if not LADDER_LOG.exists():
        return []
    with LADDER_LOG.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _matching_rows(
    brain: str,
    deck_path: str,
    families: dict[str, list[str]],
) -> list[dict[str, str]]:
    fam = brain_family(brain, families)
    deck_stem = _stem(deck_path)
    rows = []
    for row in _load_ladder():
        if row.get("status") != "COMPLETE":
            continue
        row_fam = brain_family(row.get("agent", ""), families)
        row_deck = _stem(row.get("deck", ""))
        if row_fam == fam and row_deck == deck_stem:
            rows.append(row)
    return rows


PORT_ONLY_PHRASES = (
    "port",
    "repro",
    "reproduce",
    "verify",
    "dry-run",
    "dry run",
    "repackage",
    "same policy",
    "faithful",
)

MATERIAL_CHANGE_HINTS = (
    "lever",
    "fix",
    "guard",
    "bench",
    "matchup",
    "scorer",
    "search",
    "improve",
    "r2",
    "r7",
    "v2",
    "v3",
    "v4",
    "new deck",
    "deck swap",
    "target",
    "boss",
    "switch",
)


def _is_port_only_change(change: str) -> bool:
    c = change.lower().strip()
    if not c:
        return True
    if any(h in c for h in MATERIAL_CHANGE_HINTS):
        return False
    return any(p in c for p in PORT_ONLY_PHRASES)


def _policy_equivalent_block(name: str, change: str, final_lock_in: bool) -> tuple[bool, str]:
    for pe in POLICY_EQUIVALENT:
        if name != pe["name"] and pe["name"] not in name:
            continue
        if final_lock_in:
            return False, ""
        if _is_port_only_change(change):
            return True, (
                f"Package '{name}' is policy-equivalent to ladder ref {pe['ladder_ref']} "
                f"(@ {pe['ladder_mu']} μ). {pe['note']}"
            )
    return False, ""


def _list_manifests() -> list[Path]:
    if not CANDIDATES_DIR.is_dir():
        return []
    return sorted(CANDIDATES_DIR.glob("*.manifest.json"))


def _parse_manifest(path: Path) -> dict:
    if not path.is_file():
        rel = path
        try:
            rel = path.relative_to(ROOT)
        except ValueError:
            pass
        lines = [f"Manifest not found: {rel}"]
        found = _list_manifests()
        if found:
            lines.append("Available manifests (run package script first if missing):")
            for p in found:
                lines.append(f"  {p.relative_to(ROOT)}")
        else:
            lines.append(
                f"No manifests under {CANDIDATES_DIR.relative_to(ROOT)}. "
                "Run e.g. python scripts/package_dragapult.py first, "
                "or use --brain and --deck without --manifest."
            )
        lines.append("")
        lines.append("Example without manifest:")
        lines.append(
            '  python scripts/check_upload_eligible.py --brain LucarioScorer '
            '--deck agent_decks/real_mega_lucario_ex.csv '
            '--change "LucarioScorer: <delta>" --local-gate 58.0'
        )
        print("\n".join(lines), file=sys.stderr)
        raise SystemExit(1)
    data = json.loads(path.read_text(encoding="utf-8"))
    brain = data.get("agent", data.get("brain", ""))
    # extract module name from "agent/foo.py (...)" 
    if "/" in brain:
        brain = Path(brain.split("(")[0].strip().split()[-1]).stem
    return {
        "name": data.get("name", path.stem.replace(".manifest", "")),
        "brain": brain,
        "deck": data.get("deck", ""),
        "deck_sha1": data.get("deck_sha1"),
        "agent_sha1": data.get("agent_sha1"),
        "ladder_benchmark_ref": data.get("ladder_benchmark_ref"),
        "ladder_benchmark_mu": data.get("ladder_benchmark_mu"),
    }


def _change_describes_delta(change: str, brain: str, deck: str) -> bool:
    """True if --change looks like a material iteration, not a restatement."""
    if _is_port_only_change(change):
        return False
    c = change.lower()
    if any(h in c for h in MATERIAL_CHANGE_HINTS):
        return True
    # Must mention brain or deck stem if no keyword
    stem = _stem(deck).replace("_", " ")
    return brain.lower() in c or stem[:12] in c


def check(
    *,
    name: str,
    brain: str,
    deck: str,
    change: str,
    local_gate: float | None,
    final_lock_in: bool,
    deck_sha1: str | None = None,
    agent_sha1: str | None = None,
) -> int:
    families = _load_families()
    lines: list[str] = []
    blocked = False
    block_reason = ""

    lines.append("=== Upload eligibility (R12) ===")
    lines.append(f"Candidate: {name or brain} × {_stem(deck)}")
    lines.append(f"Brain family: {brain_family(brain, families)}")
    if change:
        lines.append(f"Hypothesis: {change}")
    else:
        lines.append("Hypothesis: (missing — required)")
        blocked = True
        block_reason = "No --change hypothesis. State what is NEW vs the last ladder row."

    # Policy-equivalent port check
    if name:
        pe_block, pe_msg = _policy_equivalent_block(name, change, final_lock_in)
        if pe_block:
            blocked = True
            block_reason = pe_msg

    # Ladder log matches
    matches = _matching_rows(brain, deck, families)
    if matches and not final_lock_in:
        best = max(matches, key=lambda r: float(r.get("mu_reading_1") or 0))
        mu = best.get("mu_reading_1", "?")
        ref = best.get("ref", "?")
        lines.append("")
        lines.append(f"PRIOR LADDER ROW: ref {ref} @ {mu} μ ({best.get('name')})")
        if not blocked and _is_port_only_change(change):
            blocked = True
            block_reason = (
                f"Same brain family × deck already COMPLETE on ladder (ref {ref}, {mu} μ). "
                "Iterate locally first; upload only with a material change."
            )
        elif not blocked and not _change_describes_delta(change, brain, deck):
            blocked = True
            block_reason = (
                "--change must name a concrete delta (lever, fix, deck, scorer) vs ref "
                f"{ref} @ {mu} μ."
            )

    fam = brain_family(brain, families)
    deck_stem = _stem(deck)

    if (
        not final_lock_in
        and deck_stem == SEARCH_LUCARIO_BENCHMARK["deck_stem"]
        and fam == "lucario_rules"
    ):
        lines.append("")
        lines.append(
            f"HOME-GROWN BAR: SearchScorer ref {SEARCH_LUCARIO_BENCHMARK['ladder_ref']} "
            f"@ {SEARCH_LUCARIO_BENCHMARK['ladder_mu']} μ on this deck — beat that, not just track_c 535.6."
        )

    # Local gate minimum for new uploads
    if local_gate is not None and not final_lock_in:
        if not blocked and local_gate < MIN_LOCAL_GATE_WR_PCT:
            blocked = True
            block_reason = (
                f"Local gate {local_gate}% < {MIN_LOCAL_GATE_WR_PCT}% minimum for a new upload. "
                "Run n≥30 full suite; iterate until WR improves materially."
            )
        elif matches:
            prior_local = matches[0].get("local_gate_overall_pct", "")
            try:
                prior_pct = float(str(prior_local).split()[0].replace("%", ""))
                if local_gate <= prior_pct:
                    lines.append(
                        f"Note: local gate {local_gate}% does not beat prior logged {prior_pct}%."
                    )
            except (ValueError, IndexError):
                pass

    if final_lock_in:
        lines.append("")
        lines.append("FINAL LOCK-IN mode: duplicate allowed near deadline for Finals selection.")

    lines.append("")
    if blocked:
        lines.append("VERDICT: BLOCKED")
        lines.append(f"Reason: {block_reason}")
        lines.append("")
        lines.append("What to do instead:")
        lines.append("  1. Local gate n≥30 vs native field — beat the prior row's WR or μ target")
        lines.append("  2. One concrete change (lever, scorer fix, deck swap) — document in --change")
        lines.append("  3. Re-run this script with --change describing the delta")
        lines.append("  4. python scripts/check_upload_eligible.py --suggest")
        for s in SUGGESTED_NEXT[:3]:
            lines.append(f"     → {s['id']}: {s['why']}")
    else:
        lines.append("VERDICT: ELIGIBLE (proceed only with user OK)")
        lines.append("")
        lines.append("Pre-upload checklist:")
        lines.append("  [ ] Dry-run package passed")
        lines.append("  [ ] Local gate n≥30 recorded (R8 metadata)")
        lines.append("  [ ] Catalog row named in commit message / Kaggle -m")
        lines.append("  [ ] python scripts/track_ladder.py after COMPLETE")
        lines.append("  [ ] 2 μ readings ≥40 min apart before pivoting (R1)")

    print("\n".join(lines))
    return 1 if blocked else 0


def suggest() -> int:
    print("=== Suggested next uploads (new catalog rows only) ===\n")
    for s in SUGGESTED_NEXT:
        print(f"{s['id']} — {s['brain']} × {s['deck']}")
        print(f"  Why: {s['why']}")
        print(f"  Beat: {s['beat_row']}")
        print(f"  Local: {s['local_gate']}")
        print()
    print(f"Full decode: {CATALOG.relative_to(ROOT)}")
    print(f"Ladder log: {LADDER_LOG.relative_to(ROOT)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, help="Package manifest JSON from dist/candidates/")
    ap.add_argument("--name", help="Package/candidate name")
    ap.add_argument("--brain", help="Brain id (e.g. LucarioScorer, alakazam_agent)")
    ap.add_argument("--deck", help="Deck CSV path")
    ap.add_argument("--change", default="", help="One-line: what is NEW vs last ladder row")
    ap.add_argument("--local-gate", type=float, help="Overall local gate WR%% (filter)")
    ap.add_argument(
        "--final-lock-in",
        action="store_true",
        help="Near deadline: re-ship best tarball for Finals selection (R12 exception)",
    )
    ap.add_argument("--suggest", action="store_true", help="List high-value next uploads")
    args = ap.parse_args()

    if args.suggest:
        return suggest()

    if args.manifest:
        m = _parse_manifest(args.manifest)
        return check(
            name=m["name"],
            brain=m["brain"],
            deck=m["deck"],
            change=args.change,
            local_gate=args.local_gate,
            final_lock_in=args.final_lock_in,
            deck_sha1=m.get("deck_sha1"),
            agent_sha1=m.get("agent_sha1"),
        )

    if not args.brain or not args.deck:
        ap.error("Provide --manifest or both --brain and --deck (or --suggest)")

    return check(
        name=args.name or "",
        brain=args.brain,
        deck=args.deck,
        change=args.change,
        local_gate=args.local_gate,
        final_lock_in=args.final_lock_in,
    )


if __name__ == "__main__":
    raise SystemExit(main())

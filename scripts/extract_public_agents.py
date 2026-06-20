"""Extract downloaded public Kaggle agents into runnable submission tarballs.

For each .ipynb under data/kaggle_ref/{community,rule_agents}, pull the
`%%writefile main.py` cell and a 60-card deck, then package
data/kaggle_ref/opponents/<slug>/{main.py,deck.csv,submission.tar.gz} in the
same layout verify_archive.load_submission expects (main.py + deck.csv + cg).

Deck resolution order:
  1. an embedded list literal assigned to DECK / my_deck / deck (>=40 ints), else
  2. a fallback map from the kiyota rule agents (deck comes from the comp dataset)
     to our matching mined real lists.

This lets us gate our candidates against the actual public field instead of
random / pool_* proxies (see report/competition_insights.md).
"""

from __future__ import annotations

import ast
import json
import shutil
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIRS = [ROOT / "data" / "kaggle_ref" / "community", ROOT / "data" / "kaggle_ref" / "rule_agents"]
OUT_DIR = ROOT / "data" / "kaggle_ref" / "opponents"
CG_DIR = ROOT / "data" / "sim" / "sample_submission" / "cg"

# kiyota rule agents read deck.csv from the competition dataset; pair with our mined real lists.
FALLBACK_DECK = {
    "a-sample-rule-based-agent-mega-lucario-ex-deck": "agent_decks/real_mega_lucario_ex.csv",
    "a-sample-rule-based-agent-dragapult-ex-deck": "agent_decks/real_dragapult_ex.csv",
    "a-sample-rule-based-agent-iono-s-deck": "agent_decks/real_iono.csv",
    "a-sample-rule-based-agent-mega-abomasnow-ex-deck": "agent_decks/real_mega_abomasnow_ex.csv",
}


def cells(nb_path: Path) -> list[str]:
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    return ["".join(c.get("source", [])) for c in nb.get("cells", []) if c.get("cell_type") == "code"]


def extract_main(srcs: list[str]) -> str | None:
    for src in srcs:
        s = src.lstrip()
        if s.startswith("%%writefile main.py"):
            # drop the magic line
            return src.split("\n", 1)[1] if "\n" in src else ""
    return None


def _int_list(node: ast.AST) -> list[int] | None:
    if not isinstance(node, (ast.List, ast.Tuple)):
        return None
    out = []
    for elt in node.elts:
        if isinstance(elt, ast.Constant) and isinstance(elt.value, int):
            out.append(elt.value)
        else:
            return None
    return out


def extract_deck(srcs: list[str]) -> list[int] | None:
    # 1. a `%%writefile deck.csv` cell — body is 60 lines of card ids.
    for src in srcs:
        if src.lstrip().startswith("%%writefile deck.csv"):
            body = src.split("\n", 1)[1] if "\n" in src else ""
            ids = [int(x) for x in body.splitlines() if x.strip().lstrip("-").isdigit()]
            if len(ids) >= 40:
                return ids
    # 2. an embedded list literal.
    names = {"DECK", "my_deck", "deck", "MY_DECK", "deck_list"}
    for src in srcs:
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name) and tgt.id in names:
                        lst = _int_list(node.value)
                        if lst and len(lst) >= 40:
                            return lst
    return None


def load_csv_deck(rel: str) -> list[int]:
    p = ROOT / rel
    return [int(x) for x in p.read_text().splitlines() if x.strip()]


def package(slug: str, main_py: str, deck: list[int]) -> Path:
    d = OUT_DIR / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "main.py").write_text(main_py, encoding="utf-8")
    (d / "deck.csv").write_text("\n".join(map(str, deck)) + "\n", encoding="utf-8")
    tar_path = d / "submission.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(d / "main.py", arcname="main.py")
        tar.add(d / "deck.csv", arcname="deck.csv")
        for item in sorted(CG_DIR.rglob("*")):
            if item.is_file() and "__pycache__" not in item.parts and item.suffix not in {".pyc", ".pyo"}:
                tar.add(item, arcname=str(Path("cg") / item.relative_to(CG_DIR)))
    return tar_path


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    nbs = []
    for d in SRC_DIRS:
        nbs.extend(sorted(d.glob("*.ipynb")))
    ok, skipped = [], []
    for nb in nbs:
        slug = nb.stem
        srcs = cells(nb)
        main_py = extract_main(srcs)
        if not main_py:
            skipped.append((slug, "no main.py cell"))
            continue
        deck = extract_deck(srcs)
        src_kind = "embedded"
        if deck is None or len(deck) != 60:
            rel = FALLBACK_DECK.get(slug)
            if rel and (ROOT / rel).exists():
                deck = load_csv_deck(rel)
                src_kind = f"fallback:{rel}"
            else:
                skipped.append((slug, f"no 60-card deck (got {len(deck) if deck else 0})"))
                continue
        tar = package(slug, main_py, deck)
        ok.append((slug, len(deck), src_kind, tar.stat().st_size))
        print(f"OK   {slug}  deck={len(deck)} [{src_kind}]  {tar.stat().st_size} bytes")
    print("\n=== skipped ===")
    for slug, why in skipped:
        print(f"SKIP {slug}: {why}")
    print(f"\nextracted {len(ok)}/{len(nbs)} agents -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

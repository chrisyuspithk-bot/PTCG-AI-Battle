"""Import a Kaggle notebook candidate that uses %%writefile cells.

This is meant for public baseline notebooks that write ``main.py`` and
``deck.csv`` before creating ``submission.tar.gz``. It extracts those files,
copies the local simulator ``cg`` package, and builds a normal candidate
archive under ``dist/candidates``.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE_CG = ROOT / "data" / "sim" / "sample_submission" / "cg"


def _cell_source(cell: dict) -> str:
    source = cell.get("source", "")
    if isinstance(source, list):
        return "".join(source)
    return str(source)


def extract_writefile_cells(notebook: Path) -> dict[str, str]:
    data = json.loads(notebook.read_text(encoding="utf-8"))
    files: dict[str, str] = {}
    for cell in data.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = _cell_source(cell)
        lines = source.splitlines()
        if not lines:
            continue
        first = lines[0].strip()
        if not first.startswith("%%writefile "):
            continue
        parts = first.split(maxsplit=1)
        if len(parts) != 2:
            continue
        name = parts[1].strip()
        files[name] = "\n".join(lines[1:]).rstrip() + "\n"
    return files


def copytree_clean(src: Path, dst: Path) -> None:
    def ignore(_dir: str, names: list[str]) -> set[str]:
        return {n for n in names if n == "__pycache__" or n.endswith(".pyc")}

    shutil.copytree(src, dst, ignore=ignore)


def normalize_main_py(content: str) -> str:
    """Make notebook-style submissions work in local import-based verifiers."""
    old = '''# Load deck.csv in the dataset
file_path = "deck.csv"
if not os.path.exists(file_path):
    file_path = "/kaggle_simulations/agent/" + file_path
with open(file_path, "r") as file:
    csv = file.read().split("\\n")
my_deck = []
for i in range(60):
    my_deck.append(int(csv[i]))
'''
    new = '''# Load deck.csv in Kaggle or local archive-verification contexts.
_deck_candidates = []
try:
    _deck_candidates.append(os.path.join(os.path.dirname(__file__), "deck.csv"))
except NameError:
    pass
_deck_candidates.extend([
    "deck.csv",
    "/kaggle_simulations/agent/deck.csv",
])
for file_path in _deck_candidates:
    if os.path.exists(file_path):
        break
else:
    raise FileNotFoundError("deck.csv")
with open(file_path, "r") as file:
    csv = file.read().split("\\n")
my_deck = []
for i in range(60):
    my_deck.append(int(csv[i]))
'''
    if old in content:
        return content.replace(old, new)
    return content


def build_candidate(notebook: Path, name: str) -> Path:
    if not ENGINE_CG.exists():
        raise FileNotFoundError(f"missing simulator cg directory: {ENGINE_CG}")
    files = extract_writefile_cells(notebook)
    missing = {"main.py", "deck.csv"} - set(files)
    if missing:
        raise RuntimeError(f"{notebook} missing %%writefile cells: {sorted(missing)}")

    build_dir = ROOT / "dist" / "notebook_candidates" / name
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    for rel, content in files.items():
        if Path(rel).name != rel:
            raise RuntimeError(f"refusing nested writefile path: {rel}")
        if rel == "main.py":
            content = normalize_main_py(content)
        (build_dir / rel).write_text(content, encoding="utf-8")
    copytree_clean(ENGINE_CG, build_dir / "cg")

    archive = ROOT / "dist" / "candidates" / f"{name}.tar.gz"
    archive.parent.mkdir(parents=True, exist_ok=True)
    if archive.exists():
        archive.unlink()
    with tarfile.open(archive, "w:gz") as tar:
        for path in sorted(p for p in build_dir.rglob("*") if p.is_file()):
            tar.add(path, arcname=path.relative_to(build_dir).as_posix())
    return archive


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebook", type=Path)
    parser.add_argument("--name", required=True)
    args = parser.parse_args(argv)

    notebook = args.notebook if args.notebook.is_absolute() else ROOT / args.notebook
    archive = build_candidate(notebook, args.name)
    print(archive.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

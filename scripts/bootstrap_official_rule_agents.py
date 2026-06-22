"""Build agent/iono_agent.py and agent/abomasnow_agent.py from official samples.

Source order (first hit wins):
  1. data/kaggle_ref/opponents/<slug>/main.py  (from extract_public_agents.py)
  2. notebooks/official/sample_*/**.ipynb      (from fetch_official_rule_samples.ps1)

Lucario and Dragapult already live in agent/lucario_policy.py and agent/dragapult_agent.py.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPP_DIR = ROOT / "data" / "kaggle_ref" / "opponents"
NOTEBOOK_DIRS = [
    ROOT / "notebooks" / "official",
    ROOT / "notebooks",
]

AGENT_SPECS = (
    {
        "slug": "a-sample-rule-based-agent-iono-s-deck",
        "notebook_stems": ("sample_iono", "a-sample-rule-based-agent-iono-s-deck"),
        "out": "agent/iono_agent.py",
        "env_var": "IONO_DECK",
        "default_deck": "real_iono.csv",
        "title": "Iono official sample",
    },
    {
        "slug": "a-sample-rule-based-agent-mega-abomasnow-ex-deck",
        "notebook_stems": ("sample_abomasnow", "a-sample-rule-based-agent-mega-abomasnow-ex-deck"),
        "out": "agent/abomasnow_agent.py",
        "env_var": "ABOMASNOW_DECK",
        "default_deck": "real_mega_abomasnow_ex.csv",
        "title": "Mega Abomasnow ex official sample",
    },
)

WRAPPER_HEAD = '''"""{title} - official Kaggle sample (never-crash wrapper).

Deck path: env {env_var} or deck.csv in cwd.
Built by scripts/bootstrap_official_rule_agents.py - re-run after kernel updates.
"""

'''

WRAPPER_TAIL = '''

def _resolve_deck_path() -> str:
    env = os.environ.get("{env_var}")
    if env and os.path.exists(env):
        return env
    if os.path.exists("deck.csv"):
        return "deck.csv"
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "..", "agent_decks", "{default_deck}")


with open(_resolve_deck_path(), "r", encoding="utf-8") as file:
    _csv = file.read().split("\\n")
my_deck = [int(_csv[i]) for i in range(60)]


def _legal_fallback(obs_dict: dict) -> list[int]:
    sel = obs_dict.get("select")
    if sel is None:
        return my_deck
    n = len(sel.get("option", []))
    min_c = int(sel.get("minCount") or 0)
    max_c = int(sel.get("maxCount") or 0)
    if n == 0 or max_c == 0:
        return []
    k = min_c if min_c > 0 else min(1, max_c)
    k = min(k, max_c, n)
    return list(range(k))


def _is_legal(out, obs_dict: dict) -> bool:
    sel = obs_dict.get("select")
    if sel is None:
        return isinstance(out, list) and len(out) == 60
    if not isinstance(out, list):
        return False
    n = len(sel.get("option", []))
    min_c = int(sel.get("minCount") or 0)
    max_c = int(sel.get("maxCount") or 0)
    if len(out) != len(set(out)):
        return False
    if not all(isinstance(i, int) and 0 <= i < n for i in out):
        return False
    return min_c <= len(out) <= max_c


def agent(obs_dict: dict) -> list[int]:
    out, fellback = None, False
    try:
        out = _agent_impl(obs_dict)
        if not _is_legal(out, obs_dict):
            out, fellback = _legal_fallback(obs_dict), True
    except Exception:
        out, fellback = _legal_fallback(obs_dict), True
    return out
'''


def cells(nb_path: Path) -> list[str]:
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    return ["".join(c.get("source", [])) for c in nb.get("cells", []) if c.get("cell_type") == "code"]


def extract_main_from_notebook(srcs: list[str]) -> str | None:
    for src in srcs:
        if src.lstrip().startswith("%%writefile main.py"):
            return src.split("\n", 1)[1] if "\n" in src else ""
    return None


def rename_impl(main_py: str) -> str:
    """main.py uses `def agent` - rename to `_agent_impl` for wrapper."""
    if re.search(r"^def agent\s*\(", main_py, flags=re.M):
        return re.sub(r"^def agent\s*\(", "def _agent_impl(", main_py, count=1, flags=re.M)
    if re.search(r"^def _agent_impl\s*\(", main_py, flags=re.M):
        return main_py
    raise ValueError("main.py has no def agent(...) entry point")


def strip_embedded_deck_load(main_py: str) -> str:
    """Extracted main.py loads deck.csv at import; wrapper owns my_deck instead."""
    pat = re.compile(
        r"# Load deck\.csv in the dataset\s*\n"
        r'file_path = "deck\.csv"\s*\n'
        r"if not os\.path\.exists\(file_path\):\s*\n"
        r'    file_path = "/kaggle_simulations/agent/" \+ file_path\s*\n'
        r'with open\(file_path, "r"\) as file:\s*\n'
        r'    csv = file\.read\(\)\.split\("\\n"\)\s*\n'
        r"my_deck = \[\]\s*\n"
        r"for i in range\(60\):\s*\n"
        r"    my_deck\.append\(int\(csv\[i\]\)\)\s*\n",
        re.MULTILINE,
    )
    stripped, n = pat.subn("", main_py, count=1)
    if n == 0:
        raise ValueError("could not strip embedded deck load block from main.py")
    return stripped


def find_notebook(stems: tuple[str, ...]) -> Path | None:
    for stem in stems:
        for base in NOTEBOOK_DIRS:
            if not base.is_dir():
                continue
            for nb in base.rglob("*.ipynb"):
                if nb.stem == stem or stem in nb.stem:
                    return nb
    return None


def load_main_source(spec: dict) -> tuple[str, str] | None:
    extracted = OPP_DIR / spec["slug"] / "main.py"
    if extracted.is_file():
        return extracted.read_text(encoding="utf-8"), str(extracted.relative_to(ROOT))

    nb = find_notebook(spec["notebook_stems"])
    if nb is not None:
        main_py = extract_main_from_notebook(cells(nb))
        if main_py:
            return main_py, nb.name

    return None


def bootstrap_one(spec: dict) -> bool:
    loaded = load_main_source(spec)
    if loaded is None:
        print(f"SKIP {spec['slug']}: no extracted main.py or notebook")
        return False
    main_py, src_label = loaded
    body = strip_embedded_deck_load(rename_impl(main_py))
    text = (
        WRAPPER_HEAD.format(title=spec["title"], env_var=spec["env_var"])
        + body
        + WRAPPER_TAIL.format(env_var=spec["env_var"], default_deck=spec["default_deck"])
    )
    out = ROOT / spec["out"]
    out.write_text(text, encoding="utf-8")
    print(f"OK   {spec['out']} <- {src_label}")
    return True


def main() -> int:
    ok = sum(int(bootstrap_one(spec)) for spec in AGENT_SPECS)
    if ok == 0:
        print(
            "\nNo agents written. Run one of:\n"
            "  python scripts/extract_public_agents.py   (if rule notebooks already in repo)\n"
            "  powershell -File scripts/fetch_official_rule_samples.ps1  (needs Kaggle API)"
        )
        return 1
    print(f"\nWrote {ok}/{len(AGENT_SPECS)} standalone agents under agent/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

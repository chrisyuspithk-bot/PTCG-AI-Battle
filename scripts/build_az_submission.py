"""Build a Kaggle submission from an az_train.py-trained AlphaZero model.

The submission `main.py` reuses the *verbatim* model + encoders + MCTS code from
`rl/az_train.py` (sliced out, not re-typed, so inference matches training exactly)
and adds an `agent(obs_dict) -> list[int]` entrypoint that loads `model.pth` +
`deck.csv` and returns `mcts_agent(...)[0]` (the engine Search-API move).

No Kaggle upload here; this only assembles the package directory + tarball.
"""
from __future__ import annotations

import argparse
import shutil
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HEADER = '''\
"""AlphaZero + MCTS submission (engine Search API). Built by scripts/build_az_submission.py.

Model/encoder/MCTS code is sliced verbatim from rl/az_train.py so submission-time
inference is identical to training. Entrypoint: agent(obs_dict) -> list[int].
"""
import os
import sys
import math
import random


def _bootstrap_engine() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (here, "/kaggle_simulations/agent", "."):
        if os.path.isdir(os.path.join(cand, "cg")) and cand not in sys.path:
            sys.path.insert(0, cand)
            return


_bootstrap_engine()

import torch  # noqa: E402

from cg.api import (  # noqa: E402
    AreaType,
    Card,
    Observation,
    OptionType,
    PlayerState,
    Pokemon,
    SearchState,
    SelectContext,
    all_attack,
    all_card_data,
    search_begin,
    search_end,
    search_step,
    to_observation_class,
)

# ===================== verbatim model + MCTS (sliced from rl/az_train.py) =====================
'''

FOOTER = '''
# ===================== submission entrypoint =====================
_HERE = os.path.dirname(os.path.abspath(__file__))


def _find(name):
    for cand in (os.path.join(_HERE, name), name, "/kaggle_simulations/agent/" + name):
        if os.path.exists(cand):
            return cand
    raise FileNotFoundError(name)


def _load_deck():
    ids = [int(x.strip()) for x in open(_find("deck.csv")).read().splitlines() if x.strip()]
    if len(ids) != 60:
        raise ValueError("deck.csv must have 60 cards, got %d" % len(ids))
    return ids


my_deck = _load_deck()
_DEVICE = torch.device("cpu")
model = MyModel(__D_MODEL__, __NUM_HEADS__, __D_FF__, __ENC_LAYERS__, __DEC_LAYERS__).to(_DEVICE)
model.load_state_dict(torch.load(_find("model.pth"), map_location=_DEVICE))
model.eval()

SEARCH_COUNT = __SEARCH_COUNT__


def agent(obs_dict):
    obs = to_observation_class(obs_dict)
    if obs.select is None:
        return my_deck
    with torch.inference_mode():
        selected, _ = mcts_agent(obs_dict, my_deck, model, SEARCH_COUNT)
    return selected
'''


def _slice_body() -> str:
    """Extract from the '# ---- card/attack vocab' marker through the end of mcts_agent()."""
    src = (ROOT / "rl" / "az_train.py").read_text().splitlines()
    start = next(i for i, l in enumerate(src) if l.startswith("# ---- card/attack vocab"))
    # end: the line after the last line of mcts_agent (the next top-level `class LearnInput`)
    end = next(i for i, l in enumerate(src) if l.startswith("class LearnInput"))
    return "\n".join(src[start:end]).rstrip() + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="report/az/lucario_ex_az/model_final.pth")
    ap.add_argument("--deck", default="agent_decks/real_mega_lucario_ex.csv")
    ap.add_argument("--name", default="track_e_az_lucario")
    ap.add_argument("--search-count", type=int, default=25)
    ap.add_argument("--d-model", type=int, default=128)
    ap.add_argument("--num-heads", type=int, default=2)
    ap.add_argument("--enc-layers", type=int, default=1)
    ap.add_argument("--dec-layers", type=int, default=1)
    args = ap.parse_args(argv)

    build_dir = ROOT / "build" / args.name
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    # cg engine (the search-API-capable vendored copy)
    shutil.copytree(ROOT / "data" / "sim" / "sample_submission" / "cg", build_dir / "cg",
                    ignore=shutil.ignore_patterns("__pycache__"))
    # deck + model
    shutil.copy(ROOT / args.deck, build_dir / "deck.csv")
    shutil.copy(ROOT / args.model, build_dir / "model.pth")

    body = _slice_body()
    footer = (FOOTER
              .replace("__D_MODEL__", str(args.d_model))
              .replace("__NUM_HEADS__", str(args.num_heads))
              .replace("__D_FF__", str(args.d_model * 2))
              .replace("__ENC_LAYERS__", str(args.enc_layers))
              .replace("__DEC_LAYERS__", str(args.dec_layers))
              .replace("__SEARCH_COUNT__", str(args.search_count)))
    (build_dir / "main.py").write_text(HEADER + body + footer)

    # tarball
    dist = ROOT / "dist" / "candidates"
    dist.mkdir(parents=True, exist_ok=True)
    tar_path = dist / (args.name + ".tar.gz")
    with tarfile.open(tar_path, "w:gz") as tf:
        for item in build_dir.iterdir():
            tf.add(item, arcname=item.name)

    print("BUILT", build_dir)
    print("ARCHIVE", tar_path, f"({tar_path.stat().st_size // 1024} KiB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

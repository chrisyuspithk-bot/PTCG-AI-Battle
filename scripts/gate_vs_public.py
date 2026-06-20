"""Gate a candidate agent against the real public-agent field.

Replaces random / pool_* proxy gating (which does not predict ladder) with
head-to-head matches vs the downloaded top public agents in
data/kaggle_ref/opponents/ (see report/competition_insights.md).

Each agent is a directory or submission.tar.gz containing main.py + deck.csv.
Both agents share the one native cg engine (only one game runs at a time); each
main.py is loaded as its own module so their globals (plan/pre_turn/...) don't
collide, and deck.csv is read with cwd set to that agent's dir.

Usage:
  python scripts/gate_vs_public.py --agent dist/candidates/track_a_lucario_ex_search.tar.gz --games 30
  python scripts/gate_vs_public.py --agent data/kaggle_ref/opponents/pokemon-tcg-ai-battle-1084-5-baseline --games 30
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
import tarfile
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = ROOT / "data" / "sim" / "sample_submission"
OPP_DIR = ROOT / "data" / "kaggle_ref" / "opponents"

if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from cg.api import to_observation_class  # noqa: E402
from cg.game import battle_finish, battle_select, battle_start  # noqa: E402


def _resolve_dir(path: Path, stack: list) -> Path:
    """Return a directory holding main.py + deck.csv (extract tarball if needed)."""
    if path.is_dir():
        return path
    if path.suffix == ".gz" or path.name.endswith(".tar.gz"):
        tmp = tempfile.mkdtemp(prefix="agent_")
        stack.append(tmp)
        with tarfile.open(path, "r:gz") as tar:
            tar.extractall(tmp)
        return Path(tmp)
    raise ValueError(f"cannot resolve agent path: {path}")


def load_agent(path: Path, stack: list):
    """Load main.py from a dir/tarball as a unique module; return (agent_fn, deck, label)."""
    d = _resolve_dir(path, stack).resolve()  # absolute, so chdir(d) can't re-double the path
    main_py = d / "main.py"
    if not main_py.exists():
        raise FileNotFoundError(f"no main.py in {d}")
    cwd = os.getcwd()
    os.chdir(d)  # so module-level `open("deck.csv")` resolves
    sys.path.insert(0, str(d))  # so a bundled `agent` package / cg resolves (cg already cached)
    try:
        mod_name = f"agent_{uuid.uuid4().hex}"
        spec = importlib.util.spec_from_file_location(mod_name, main_py)
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
    finally:
        os.chdir(cwd)
        # drop bundled `agent`/cg package modules so the next candidate re-imports its own
        for name in [n for n in sys.modules if n == "agent" or n.startswith("agent.")]:
            del sys.modules[name]
        try:
            sys.path.remove(str(d))
        except ValueError:
            pass
    deck = list(getattr(module, "my_deck", None) or getattr(module, "DECK", None) or
                [int(x) for x in (d / "deck.csv").read_text().splitlines() if x.strip()])
    return module.agent, deck, path.name.replace(".tar.gz", "")


def play(agent0, deck0, agent1, deck1, max_steps: int):
    """Return winner index (0/1), 2=draw, or -1 unfinished/error."""
    obs = None
    try:
        obs, start = battle_start(deck0, deck1)
        if obs is None or start.errorPlayer >= 0:
            return -1
        for _ in range(max_steps + 1):
            obc = to_observation_class(obs)
            if obc.current.result >= 0:
                return obc.current.result
            active = agent0 if obc.current.yourIndex == 0 else agent1
            obs = battle_select(active(obs))
        return -1
    except Exception as exc:  # one bad game shouldn't abort the gate
        print(f"      [game error] {type(exc).__name__}: {exc}", flush=True)
        return -1
    finally:
        if obs is not None:
            battle_finish()


def _play_matchup(agent_path: str, opp_dir: str, games: int, max_steps: int) -> tuple[int, int, int, int]:
    """Play one matchup in THIS process; returns (w, l, d, u). Used by the subprocess child."""
    stack: list = []
    our_agent, our_deck, _ = load_agent(Path(agent_path), stack)
    opp_agent, opp_deck, _ = load_agent(Path(opp_dir), stack)
    w = l = d = u = 0
    for i in range(games):
        if i % 2 == 0:
            r = play(our_agent, our_deck, opp_agent, opp_deck, max_steps)
            ours = 0
        else:
            r = play(opp_agent, opp_deck, our_agent, our_deck, max_steps)
            ours = 1
        if r == -1:
            u += 1
        elif r == 2:
            d += 1
        elif r == ours:
            w += 1
        else:
            l += 1
    import shutil
    for tmp in stack:
        shutil.rmtree(tmp, ignore_errors=True)
    return w, l, d, u


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--agent", required=True, help="our candidate dir or submission.tar.gz")
    ap.add_argument("--games", type=int, default=30, help="games per opponent (side-swapped)")
    ap.add_argument("--max-steps", type=int, default=6000)
    ap.add_argument("--opponents-dir", default=str(OPP_DIR))
    ap.add_argument("--only", default=None, help="substring filter on opponent name")
    ap.add_argument("--matchup", default=None, help="(child) single opponent dir; prints RESULT line")
    args = ap.parse_args(argv)

    # child mode: play one matchup, print a parseable result, exit (isolates native crashes).
    if args.matchup:
        w, l, d, u = _play_matchup(args.agent, args.matchup, args.games, args.max_steps)
        print(f"RESULT {w} {l} {d} {u}", flush=True)
        return 0

    import subprocess
    opp_dirs = sorted(p for p in Path(args.opponents_dir).iterdir() if p.is_dir())
    if args.only:
        opp_dirs = [p for p in opp_dirs if args.only in p.name]

    print(f"candidate: {Path(args.agent).name.replace('.tar.gz','')}")
    print(f"field: {len(opp_dirs)} opponents, {args.games} games each (subprocess-isolated)\n")

    rows = []
    total_w = total_n = 0
    for opp_path in opp_dirs:
        cmd = [sys.executable, str(Path(__file__)), "--agent", args.agent,
               "--games", str(args.games), "--max-steps", str(args.max_steps),
               "--matchup", str(opp_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        line = next((ln for ln in proc.stdout.splitlines() if ln.startswith("RESULT ")), None)
        if line is None:
            print(f"  CRASH vs {opp_path.name}  (engine died; counted as unplayed)", flush=True)
            rows.append((opp_path.name, 0, 0, 0, args.games, None))
            continue
        _, w, l, d, u = line.split()
        w, l, d, u = int(w), int(l), int(d), int(u)
        decided = w + l
        wr = w / decided if decided else None
        total_w += w
        total_n += decided
        rows.append((opp_path.name, w, l, d, u, wr))
        wr_s = f"{wr:5.1%}" if wr is not None else "  n/a"
        print(f"  {wr_s}  vs {opp_path.name:52s}  W{w} L{l} D{d} U{u}", flush=True)

    suite_wr = total_w / total_n if total_n else 0.0
    scored = [r for r in rows if r[5] is not None]
    print(f"\n=== SUITE MEAN: {suite_wr:.1%}  ({total_w}/{total_n} decided) ===")
    if scored:
        print(f"=== per-matchup mean: {sum(r[5] for r in scored)/len(scored):.1%} over {len(scored)} opponents ===")
    losing = [r for r in scored if r[5] < 0.5]
    if losing:
        print("worst matchups:")
        for name, w, l, dd, uu, wr in sorted(losing, key=lambda x: x[5])[:8]:
            print(f"  {wr:5.1%}  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

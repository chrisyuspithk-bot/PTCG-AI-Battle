"""Starmie / Froslass — rule pilot (gold-medal pattern).

Based on ashleysandlin Limitless list + community write-up:
  generic scoring, matchup modules, finish-mode cg search, PrizeTracker for deck search.

Deck: env STARMIE_DECK, deck.csv in cwd, or repo default.
"""

from __future__ import annotations

import os
import random
import sys

try:
    ROOT = __file__
except NameError:
    ROOT = None
CG_PATH = "/kaggle_simulations/agent"
for p in ([os.path.dirname(os.path.abspath(ROOT))] if ROOT else []) + [CG_PATH]:
    if p and p not in sys.path and os.path.isdir(p):
        sys.path.insert(0, p)

from cg.api import (
    AreaType,
    CardType,
    LogType,
    OptionType,
    SelectContext,
    all_card_data,
    to_observation_class,
)

try:
    from cg.api import all_attack
    ALL_ATTACKS = {a.attackId: a for a in all_attack()}
except Exception:
    ALL_ATTACKS = {}

try:
    from agent.finish_search import try_cg_search
    from agent.prize_tracker import PrizeTracker
except ImportError:
    from finish_search import try_cg_search
    from prize_tracker import PrizeTracker

# ── Card IDs ──

STARYU = 1030
MEGA_STARMIE_EX = 1031
SNORUNT = 860
MEGA_FROSLASS_EX = 861

WATER_ENERGY = 3
LEGACY_ENERGY = 12
IGNITION_ENERGY = 17
MIST_ENERGY = 11

LILLIE = 1227
SALVATORE = 1189
WALLY = 1229
HILDA = 1225
BOSS = 1182
BLACK_BELT = 1211
POFFIN = 1086
ENERGY_SEARCH = 1119
POKEGEAR = 1122
MEGA_SIGNAL = 1145
SWITCH = 1123
NIGHT_STRETCHER = 1097
GRAVITY_MOUNTAIN = 1252

JETTING_BLOW = 1487
NEBULA_BEAM = 1488
RESENTFUL_REFRAIN = 1240

LUCARIO_LINE = {673, 674, 676, 677, 678}
DRAGAPULT_LINE = {119, 120, 121}
IONO_LINE = {265, 268, 269, 270, 271}
CRUSTLE_LINE = {344, 345}
ARCHALUDON_LINE = {169, 190}

STARMIE_LINE = {STARYU, MEGA_STARMIE_EX}
FROSLASS_LINE = {SNORUNT, MEGA_FROSLASS_EX}

CARD_DB = {c.cardId: c for c in all_card_data()}

_prize_tracker: PrizeTracker | None = None
_finish_line: list[int] | None = None


def _resolve_deck_path() -> str:
    env = os.environ.get("STARMIE_DECK")
    if env and os.path.exists(env):
        return env
    if os.path.exists("deck.csv"):
        return "deck.csv"
    try:
        here = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        here = None
    if here:
        packaged = os.path.join(here, "deck.csv")
        if os.path.exists(packaged):
            return packaged
        repo_default = os.path.join(here, "..", "agent_decks", "starmie_froslass_ashleysandlin.csv")
        if os.path.exists(repo_default):
            return repo_default
    return "/kaggle_simulations/agent/deck.csv"


with open(_resolve_deck_path(), "r", encoding="utf-8") as file:
    _csv = file.read().split("\n")
my_deck = [int(_csv[i]) for i in range(60)]

_prize_tracker = PrizeTracker(my_deck)


# ── Board helpers ──


def my_index(obs):
    return obs.current.yourIndex


def my_state(obs):
    return obs.current.players[my_index(obs)]


def opp_state(obs):
    return obs.current.players[1 - my_index(obs)]


def active_pokemon(obs, player_index=None):
    pi = player_index if player_index is not None else my_index(obs)
    ps = obs.current.players[pi]
    for p in ps.active or []:
        if p is not None:
            return p
    return None


def bench_pokemon(obs, player_index=None):
    pi = player_index if player_index is not None else my_index(obs)
    return [p for p in (obs.current.players[pi].bench or []) if p is not None]


def all_my_pokemon(obs):
    out = []
    a = active_pokemon(obs)
    if a:
        out.append(a)
    out.extend(bench_pokemon(obs))
    return out


def opp_active(obs):
    return active_pokemon(obs, 1 - my_index(obs))


def opp_bench(obs):
    return bench_pokemon(obs, 1 - my_index(obs))


def hand_ids(obs):
    return [c.id for c in (my_state(obs).hand or []) if c is not None]


def energy_count(pokemon):
    if pokemon is None:
        return 0
    return len(getattr(pokemon, "energyCards", None) or getattr(pokemon, "energies", None) or [])


def water_on(pokemon):
    if pokemon is None:
        return 0
    n = 0
    for c in getattr(pokemon, "energyCards", None) or getattr(pokemon, "energies", None) or []:
        if c and c.id == WATER_ENERGY:
            n += 1
    return n


def prize_value(pokemon):
    if pokemon is None:
        return 0
    data = CARD_DB.get(pokemon.id)
    if data is None:
        return 1
    return max(1, int(getattr(data, "prize", 1) or 1))


def damage_on(pokemon):
    if pokemon is None:
        return 0
    hp = getattr(pokemon, "hp", 0) or 0
    max_hp = getattr(pokemon, "maxHp", hp) or hp
    return max(0, max_hp - hp)


def option_card(obs, opt):
    if getattr(opt, "cardId", None):
        return None
    idx = getattr(opt, "index", None)
    area = getattr(opt, "area", None)
    pi = getattr(opt, "playerIndex", my_index(obs))
    if idx is None or area is None:
        return None
    ps = obs.current.players[pi]
    match area:
        case AreaType.HAND:
            hand = ps.hand or []
            return hand[idx] if 0 <= idx < len(hand) else None
        case AreaType.DISCARD:
            disc = ps.discard or []
            return disc[idx] if 0 <= idx < len(disc) else None
        case AreaType.DECK:
            deck = obs.select.deck or []
            return deck[idx] if obs.select and 0 <= idx < len(deck) else None
        case AreaType.ACTIVE:
            act = ps.active or []
            return act[idx] if 0 <= idx < len(act) else None
        case AreaType.BENCH:
            bench = ps.bench or []
            return bench[idx] if 0 <= idx < len(bench) else None
    return None


def option_target(obs, opt):
    area = getattr(opt, "inPlayArea", None)
    idx = getattr(opt, "inPlayIndex", 0) or 0
    pi = getattr(opt, "playerIndex", my_index(obs))
    if area is None:
        return None
    ps = obs.current.players[pi]
    match area:
        case AreaType.ACTIVE:
            act = ps.active or []
            return act[idx] if 0 <= idx < len(act) else None
        case AreaType.BENCH:
            bench = ps.bench or []
            return bench[idx] if 0 <= idx < len(bench) else None
    return None


def visible_opp_ids(obs):
    ids = set()
    for p in [opp_active(obs)] + opp_bench(obs):
        if p:
            ids.add(p.id)
    return ids


def detect_matchup(obs):
    ids = visible_opp_ids(obs)
    if ids & LUCARIO_LINE:
        return "lucario"
    if ids & CRUSTLE_LINE:
        return "crustle"
    if ids & IONO_LINE:
        return "iono"
    if ids & DRAGAPULT_LINE:
        return "dragapult"
    if ids & ARCHALUDON_LINE:
        return "archaludon"
    if ids & STARMIE_LINE:
        return "mirror"
    return "generic"


def attack_damage(attack_id: int) -> int:
    atk = ALL_ATTACKS.get(attack_id)
    return int(getattr(atk, "damage", 0) or 0) if atk else 0


def can_jetting_ko(active, target):
    if active is None:
        return False
    # Jetting: 120 to active
    return attack_damage(JETTING_BLOW) >= target.hp


def prized_penalty(card_id: int) -> float:
    if _prize_tracker is None:
        return 0.0
    prized = _prize_tracker.is_prized(card_id)
    if prized is True:
        return -1e9
    return 0.0


# ── Scoring ──


def score_play(obs, opt):
    card = option_card(obs, opt)
    cid = card.id if card else getattr(opt, "cardId", 0)
    ids = hand_ids(obs)
    matchup = detect_matchup(obs)
    my_prize = len(my_state(obs).prize or [])

    if cid in STARMIE_LINE:
        if cid == STARYU:
            return 12000, "play Staryu"
        return 8000, "play Starmie line"
    if cid in FROSLASS_LINE:
        if matchup == "lucario":
            return 6000, "play Froslass line vs Lucario"
        return 9000, "play Froslass line"

    if cid == POFFIN and len(my_state(obs).bench or []) < 5:
        return 15000, "Poffin"
    if cid == MEGA_SIGNAL:
        return 14000, "Mega Signal"
    if cid == LILLIE and not obs.current.supporterPlayed:
        return 13000, "Lillie"
    if cid == SALVATORE and not obs.current.supporterPlayed:
        return 12500, "Salvatore"
    if cid == HILDA and not obs.current.supporterPlayed:
        return 11000, "Hilda"
    if cid == WALLY and not obs.current.supporterPlayed:
        active = active_pokemon(obs)
        if active and active.id in (MEGA_STARMIE_EX, MEGA_FROSLASS_EX) and damage_on(active) > 0:
            return 16000, "Wally heal mega"
        return 4000, "Wally"
    if cid == BOSS and not obs.current.supporterPlayed:
        return _score_boss_play(obs)
    if cid == BLACK_BELT and not obs.current.supporterPlayed:
        return 10000, "Black Belt"
    if cid == ENERGY_SEARCH:
        return 9000, "Energy Search"
    if cid == POKEGEAR and not obs.current.supporterPlayed:
        return 8500, "Pokegear"
    if cid == SWITCH:
        return 7000, "Switch"
    if cid == NIGHT_STRETCHER:
        return 7500, "Night Stretcher"
    if cid == GRAVITY_MOUNTAIN:
        if matchup in ("lucario", "crustle", "dragapult"):
            return 11000, "Gravity Mountain"
        return 5000, "Gravity Mountain"
    if cid == WATER_ENERGY:
        return 3000, "play Water"
    return 1000, "generic play"


def _score_boss_play(obs):
    remaining = len(my_state(obs).prize or [])
    active = active_pokemon(obs)
    attacks = []
    if active and active.id == MEGA_STARMIE_EX:
        attacks = [JETTING_BLOW, NEBULA_BEAM]
    best = -500
    reason = "save Boss"
    for target in opp_bench(obs):
        for aid in attacks:
            dmg = attack_damage(aid)
            if aid == JETTING_BLOW:
                dmg = 120
            if dmg >= target.hp:
                pv = prize_value(target)
                if pv >= remaining:
                    return 25000, "LETHAL Boss"
                s = 5000 + pv * 500
                if s > best:
                    best = s
                    reason = "Boss bench KO"
    return best, reason


def score_evolve(obs, opt):
    card = option_card(obs, opt)
    target = option_target(obs, opt)
    cid = card.id if card else None
    tid = target.id if target else None
    if cid == MEGA_STARMIE_EX and tid == STARYU:
        return 20000, "evolve Starmie ex"
    if cid == MEGA_FROSLASS_EX and tid == SNORUNT:
        return 15000, "evolve Froslass ex"
    return 8000, "evolve"


def score_attach(obs, opt):
    target = option_target(obs, opt)
    if target is None:
        return 1000, "attach"
    tid = target.id
    e = energy_count(target)
    score = 1000
    if tid == MEGA_STARMIE_EX:
        score = 15000 + max(0, 3 - e) * 3000
        if e == 0:
            score += 5000
    elif tid in STARMIE_LINE:
        score = 8000 + max(0, 2 - e) * 2000
    elif tid in FROSLASS_LINE:
        score = 4000
    if getattr(opt, "inPlayArea", None) == AreaType.ACTIVE:
        score += 2000
    return score, "attach"


def score_attack(obs, opt):
    aid = getattr(opt, "attackId", 0) or 0
    active = active_pokemon(obs)
    opp = opp_active(obs)
    my_prize = len(my_state(obs).prize or [])
    matchup = detect_matchup(obs)

    if aid == JETTING_BLOW:
        if opp and can_jetting_ko(active, opp):
            return 30000, "Jetting KO"
        bench_ko = sum(1 for b in opp_bench(obs) if b.hp <= 50)
        return 18000 + bench_ko * 2000, "Jetting Blow"
    if aid == NEBULA_BEAM:
        if opp and attack_damage(NEBULA_BEAM) >= opp.hp:
            return 28000, "Nebula KO"
        if my_prize <= 2:
            return 16000, "Nebula pressure"
        return 12000, "Nebula Beam"
    if aid == RESENTFUL_REFRAIN:
        hand_sz = len(opp_state(obs).hand or [])
        dmg = 50 * hand_sz
        if opp and dmg >= opp.hp:
            return 26000, "Resentful KO"
        if matchup == "iono" and hand_sz >= 4:
            return 15000, "Resentful vs Iono hand"
        return 8000 + hand_sz * 500, "Resentful Refrain"
    return 5000, "attack"


def score_retreat(obs, opt):
    active = active_pokemon(obs)
    if active and damage_on(active) > active.hp // 2:
        return 8000, "retreat wounded"
    return -5000, "no retreat"


def score_target(obs, opt):
    card = option_card(obs, opt)
    cid = card.id if card else getattr(opt, "cardId", 0)
    ctx = obs.select.context
    matchup = detect_matchup(obs)

    if ctx in {SelectContext.TO_HAND, SelectContext.TO_DECK, SelectContext.TO_DECK_BOTTOM}:
        base = 5000
        if cid == WATER_ENERGY:
            base = 12000
        elif cid in STARMIE_LINE:
            base = 11000
        elif cid in FROSLASS_LINE:
            base = 9000
        elif cid == MEGA_STARMIE_EX:
            base = 13000
        elif cid == MEGA_FROSLASS_EX:
            base = 10000
        return base + prized_penalty(cid), "deck pick"

    if ctx == SelectContext.ATTACH_TO:
        return (12000, "Water to attacker") if cid == WATER_ENERGY else (1000, "attach pick")

    if ctx in {SelectContext.TO_FIELD, SelectContext.TO_BENCH}:
        if cid == STARYU:
            return 15000, "bench Staryu"
        if cid == SNORUNT:
            return 12000, "bench Snorunt"
        if cid == MEGA_STARMIE_EX:
            return 8000, "bench Starmie ex"
        return 5000, "to field"

    if ctx in {SelectContext.SWITCH, SelectContext.TO_ACTIVE}:
        yi = my_index(obs)
        pi = getattr(opt, "playerIndex", yi)
        if pi != yi and card:
            pv = prize_value(card)
            return 20000 + pv * 3000, "Boss target"
        if cid == MEGA_STARMIE_EX:
            return 18000, "promote Starmie ex"
        if cid == STARYU and water_on(card) >= 1:
            return 12000, "promote Staryu"
        return 5000, "promote"

    if ctx == SelectContext.HEAL:
        return damage_on(card) * 50, "heal"

    if ctx == SelectContext.DAMAGE:
        hp = getattr(card, "hp", 999) if card else 999
        return 10000 - hp, "damage target"

    return 1000 + prized_penalty(cid), "generic target"


def score_discard(obs, opt):
    card = option_card(obs, opt)
    cid = card.id if card else getattr(opt, "cardId", 0)
    if cid in (MEGA_STARMIE_EX, MEGA_FROSLASS_EX):
        return -5000, "keep mega"
    if cid == WATER_ENERGY and hand_ids(obs).count(WATER_ENERGY) <= 2:
        return -2000, "keep Water"
    return 3000, "discard"


def score_option(obs, opt):
    match opt.type:
        case OptionType.PLAY:
            return score_play(obs, opt)
        case OptionType.EVOLVE:
            return score_evolve(obs, opt)
        case OptionType.ATTACH:
            return score_attach(obs, opt)
        case OptionType.ATTACK:
            return score_attack(obs, opt)
        case OptionType.RETREAT:
            return score_retreat(obs, opt)
        case OptionType.TARGET:
            return score_target(obs, opt)
        case OptionType.DISCARD:
            return score_discard(obs, opt)
        case OptionType.END:
            return (-100, "end")
        case _:
            return (1000, "other")


def choose_options(obs, obs_dict: dict):
    global _finish_line
    options = obs.select.option or []
    if not options:
        return []

    my_prize = len(my_state(obs).prize or [])
    if my_prize <= 2 and obs_dict.get("search_begin_input"):
        finish = try_cg_search(obs_dict, options, budget_ms=250)
        if finish is not None:
            _finish_line = finish
            return finish

    scored = []
    for i, opt in enumerate(options):
        try:
            score, _ = score_option(obs, opt)
        except Exception:
            score = -999999
        scored.append((score, i))
    scored.sort(key=lambda x: (x[0], -x[1]), reverse=True)

    selected = []
    min_c = obs.select.minCount
    max_c = obs.select.maxCount
    for score, i in scored:
        if len(selected) >= max_c:
            break
        if score < 0 and len(selected) >= min_c:
            continue
        selected.append(i)
    if len(selected) < min_c:
        selected = [i for _, i in scored[:min_c]]
    return selected


def _agent_impl(obs_dict: dict) -> list[int]:
    global _finish_line
    obs = to_observation_class(obs_dict)
    if obs.select is None:
        _finish_line = None
        return my_deck

    if _prize_tracker is not None:
        _prize_tracker.update(obs, obs_dict)

    if not obs.select.option:
        return []

    # Replay verified finish line when search committed a sequence
    if _finish_line is not None:
        if len(_finish_line) <= len(obs.select.option):
            out = _finish_line
            _finish_line = None
            return out

    return choose_options(obs, obs_dict)


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


try:
    from agent.starmie_bench_guard import apply_bench_guard
except ImportError:
    from starmie_bench_guard import apply_bench_guard


def agent(obs_dict: dict) -> list[int]:
    try:
        raw = _agent_impl(obs_dict)
        bench_on = os.environ.get("STARMIE_BENCH_GUARD", "1") != "0"
        out = apply_bench_guard(obs_dict, raw) if bench_on else raw
        if not _is_legal(out, obs_dict):
            return _legal_fallback(obs_dict)
    except Exception:
        return _legal_fallback(obs_dict)
    return out

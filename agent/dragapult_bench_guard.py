"""Empty-bench guard for standalone Dragapult rules pilot (Phase 2, R7).

When bench_count == 0, force the first legal basic onto bench (setup or MAIN PLAY)
before the sample logic skips, ends, or attacks. Does not force a 2nd bench.
"""

from __future__ import annotations

from cg.api import (
    AreaType,
    CardType,
    Observation,
    OptionType,
    SelectContext,
    all_card_data,
    to_observation_class,
)

card_table = {c.cardId: c for c in all_card_data()}

# Prefer Dreepy line, then other basics in the sample list.
_BENCH_PRIORITY = (119, 235, 140, 184, 1071)


def is_basic_pokemon_id(card_id: int) -> bool:
    data = card_table.get(card_id)
    if data is None:
        return False
    return data.cardType == CardType.POKEMON and bool(getattr(data, "basic", False))


def bench_count(obs: Observation, my_index: int) -> int:
    return len(obs.current.players[my_index].bench or [])


def _get_card(obs: Observation, area: AreaType, index: int, player_index: int):
    ps = obs.current.players[player_index]
    match area:
        case AreaType.DECK:
            return obs.select.deck[index]
        case AreaType.HAND:
            return ps.hand[index]
        case AreaType.DISCARD:
            return ps.discard[index]
        case AreaType.ACTIVE:
            return ps.active[index]
        case AreaType.BENCH:
            return ps.bench[index]
        case AreaType.PRIZE:
            return ps.prize[index]
        case AreaType.STADIUM:
            return obs.current.stadium[index]
        case AreaType.LOOKING:
            return obs.current.looking[index]
        case _:
            return None


def _card_id_for_option(obs: Observation, option, my_index: int) -> int | None:
    if option.type == OptionType.CARD:
        card = _get_card(obs, option.area, option.index, option.playerIndex)
        return card.id if card is not None else None
    if option.type == OptionType.PLAY:
        card = _get_card(obs, AreaType.HAND, option.index, my_index)
        return card.id if card is not None else None
    return None


def mandatory_bench_indices(obs: Observation) -> list[int]:
    """Option indices that bench a basic when we have zero bench Pokémon."""
    if obs.select is None:
        return []
    state = obs.current
    my_index = state.yourIndex
    if bench_count(obs, my_index) > 0:
        return []

    context = obs.select.context
    out: list[int] = []
    for i, option in enumerate(obs.select.option):
        card_id = _card_id_for_option(obs, option, my_index)
        if card_id is None or not is_basic_pokemon_id(card_id):
            continue
        if context == SelectContext.SETUP_BENCH_POKEMON and option.type == OptionType.CARD:
            out.append(i)
        elif context == SelectContext.MAIN and option.type == OptionType.PLAY:
            out.append(i)
        elif context == SelectContext.TO_BENCH and option.type == OptionType.CARD:
            out.append(i)
    return out


def _best_mandatory_index(obs: Observation, indices: list[int]) -> int:
    my_index = obs.current.yourIndex

    def rank(i: int) -> tuple[int, int]:
        card_id = _card_id_for_option(obs, obs.select.option[i], my_index) or 9999
        try:
            return (_BENCH_PRIORITY.index(card_id), i)
        except ValueError:
            return (len(_BENCH_PRIORITY), i)

    return min(indices, key=rank)


def apply_bench_guard(obs_dict: dict, selection: list[int]) -> list[int]:
    """Override selection when empty bench and a mandatory basic bench is legal."""
    if obs_dict.get("select") is None:
        return selection
    if not isinstance(selection, list):
        selection = list(selection) if selection else []

    obs = to_observation_class(obs_dict)
    mandatory = mandatory_bench_indices(obs)
    if not mandatory:
        return selection
    if selection and any(i in mandatory for i in selection):
        return selection
    return [_best_mandatory_index(obs, mandatory)]

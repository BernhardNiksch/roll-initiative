import math
import random


def ability_modifier(score):
    return math.floor(score/2)-5


def _get_total(results, modifier):
    if isinstance(results, dict):
        # get total of each di size
        results = [sum(v) for k, v in results.items()]
    total_rolled = sum(results)
    return total_rolled + modifier


def _roll(faces, dice_count):
    return [random.randint(1, faces) for i in range(dice_count)]


def roll(faces, dice_count=1, modifier=0, drop_highest=0, drop_lowest=0):
    rolled = _roll(faces, dice_count)
    results = rolled
    if drop_lowest or drop_highest:
        slice_start = drop_lowest if drop_lowest > 0 else 0
        slice_stop = dice_count - (drop_highest if drop_highest > 0 else 0)
        sorted_results = sorted(rolled)
        results = sorted_results[slice_start:slice_stop]
    return {
        "rolled": rolled,
        "results": results,
        "modifier": modifier,
        "total": _get_total(results, modifier)
    }


def roll_multiple_dice(dice_dict, modifier=0):
    """roll dice of different sizes/faces"""
    results = {d: _roll(int(d), n) for d, n in dice_dict.items()}
    response = {
        "results": results,
        "modifier": modifier,
        "total": _get_total(results, modifier),
    }
    return response


def result_values_for_field(results: list, field: str) -> list:
    values = []
    field_keys = field.split("__")
    for result in results:
        value = result
        for key in field_keys:
            value = value[key]
        values.append(value)
    return values

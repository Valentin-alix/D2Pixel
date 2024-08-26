import random
from datetime import time
from time import sleep

from D2Shared.shared.utils.randomizer import pick_random_weighted_time
from src.consts import RANGE_WAIT


def convert_time_to_seconds(value: time) -> float:
    return value.hour * 3600 + value.minute * 60 + value.second


def wait(
    range: tuple[float, float] = RANGE_WAIT, is_weighted: bool = False, coeff: int = 2
):
    if is_weighted:
        wait_time = pick_random_weighted_time(*range, coeff)
    else:
        wait_time = random.uniform(*range)

    sleep(wait_time)

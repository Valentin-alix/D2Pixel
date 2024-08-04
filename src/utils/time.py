from datetime import time
from time import sleep

from D2Shared.shared.utils.randomizer import pick_random_weighted_time
from src.consts import RANGE_WAIT


def convert_time_to_seconds(value: time) -> float:
    return value.hour * 3600 + value.minute * 60 + value.second


def wait(range: tuple[float, float] = RANGE_WAIT):
    time = pick_random_weighted_time(*range)
    sleep(time)

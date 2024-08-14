from datetime import time
import random
from time import sleep

from src.consts import RANGE_WAIT


def convert_time_to_seconds(value: time) -> float:
    return value.hour * 3600 + value.minute * 60 + value.second


def wait(range: tuple[float, float] = RANGE_WAIT):
    sleep(random.uniform(*range))

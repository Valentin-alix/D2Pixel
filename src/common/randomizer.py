from EzreD2Shared.shared.utils.randomizer import pick_random_weighted_time


from time import sleep

from src.consts import RANGE_WAIT


def wait(range: tuple[float, float] = RANGE_WAIT):
    time = pick_random_weighted_time(*range)
    sleep(time)

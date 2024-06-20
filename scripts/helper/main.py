import os
import sys

sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from EzreD2Shared.shared.utils.randomizer import pick_random_weighted_time

if __name__ == "__main__":
    times = 0
    # for _ in range(1000):
    #     times += pick_random_weighted_time(0.5, 6)
    print(pick_random_weighted_time(0.5, 6))

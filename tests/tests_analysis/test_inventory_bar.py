import os
import unittest

import cv2

from src.bots.dofus.hud.small_bar import (
    get_percentage_inventory_bar_normal,
)
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_BAR = os.path.join(PATH_FIXTURES, "hud", "bar")

FOLDER_INV_BAR_PODS = os.path.join(PATH_FIXTURES_BAR, "inventory_bar")


class TestProgressBar(unittest.TestCase):
    def test_inventory_bar(self):
        RANGE_BY_FILENAME: dict[str, tuple[float, float]] = {
            "1": (0.4, 0.7),
            "2": (0.8, 1),
        }

        for filename in os.listdir(FOLDER_INV_BAR_PODS):
            img = cv2.imread(os.path.join(FOLDER_INV_BAR_PODS, filename))
            percentage = get_percentage_inventory_bar_normal(img)
            print(percentage)
            range = RANGE_BY_FILENAME[filename[:-4]]
            assert range[0] <= percentage <= range[1]

import os
import unittest

import cv2

from src.bots.dofus.hud.heart import get_heart_ratio
from tests.utils import PATH_FIXTURES

PATH_HEART_FIXTURES = os.path.join(PATH_FIXTURES, "hud", "heart")


class TestHearthBar(unittest.TestCase):
    def test_heart(self):
        RANGE_BY_FILENAME: dict[str, tuple[float, float]] = {
            "full": (0.85, 1),
            "not_full": (0.6, 85),
            "low": (0.15, 0.3),
        }

        for filename in os.listdir(PATH_HEART_FIXTURES):
            img = cv2.imread(os.path.join(PATH_HEART_FIXTURES, filename))
            ratio = get_heart_ratio(img)
            range = RANGE_BY_FILENAME[filename[:-4]]
            assert range[0] <= ratio <= range[1]

import os
import unittest

import cv2

from src.bots.dofus.hud.info_bar import (
    BarType,
    get_percentage_info_bar_fight,
    get_percentage_info_bar_normal,
)
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_BAR = os.path.join(PATH_FIXTURES, "hud", "bar")

FOLDER_BAR_PODS = os.path.join(PATH_FIXTURES_BAR, "bar_pods")

FOLDER_BAR_ENERGY = os.path.join(PATH_FIXTURES_BAR, "bar_energy")


class TestProgressBar(unittest.TestCase):
    def test_pods(self):
        RANGE_BY_FILENAME: dict[str, tuple[float, float]] = {
            "full": (0.95, 1),
            "small": (0, 0.1),
        }

        for filename in os.listdir(FOLDER_BAR_PODS):
            img = cv2.imread(os.path.join(FOLDER_BAR_PODS, filename))
            percentage = get_percentage_info_bar_normal(img, BarType.PODS)
            range = RANGE_BY_FILENAME[filename[:-4]]
            assert range[0] <= percentage <= range[1]

    def test_energy_bar(self):
        RANGE_BY_FILENAME: dict[str, tuple[float, float]] = {"full": (0.95, 1)}

        for filename in os.listdir(FOLDER_BAR_ENERGY):
            img = cv2.imread(os.path.join(FOLDER_BAR_ENERGY, filename))
            percentage = get_percentage_info_bar_normal(img)
            range = RANGE_BY_FILENAME[filename[:-4]]
            assert range[0] <= percentage <= range[1]

    def test_turn_bar(self):
        FOLDER_BAR_TURN = os.path.join(PATH_FIXTURES_BAR, "bar_turn")

        RANGE_BY_FILENAME: dict[str, tuple[float, float]] = {
            "mid": (0.4, 0.6),
            "empty": (0, 0),
            "low": (0.1, 0.4),
            "very_low": (0.1, 0.3),
        }

        for filename in os.listdir(FOLDER_BAR_TURN):
            if filename != "very_low.png":
                continue
            img = cv2.imread(os.path.join(FOLDER_BAR_TURN, filename))
            percentage = get_percentage_info_bar_fight(img)
            range = RANGE_BY_FILENAME[filename[:-4]]
            assert range[0] <= percentage <= range[1]

    def test_not_related_bar_fight(self):
        img = cv2.imread(os.path.join(FOLDER_BAR_PODS, "full.png"))
        percentage = get_percentage_info_bar_fight(img)
        assert 0 <= percentage <= 0, percentage

    def test_not_related_bar_normal(self):
        img = cv2.imread(os.path.join(FOLDER_BAR_ENERGY, "full.png"))
        percentage = get_percentage_info_bar_normal(img, BarType.PODS)
        assert 0 <= percentage <= 0, percentage

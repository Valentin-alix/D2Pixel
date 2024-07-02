import os
import unittest

import cv2
from D2Shared.shared.entities.position import Position

from src.bots.modules.harvester.harvester import clean_image_after_collect
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_HIGH = os.path.join(PATH_FIXTURES, "highlight")


class TestHighlight(unittest.TestCase):
    def test_all(self):  # MANUAL CHECK
        position_by_folder = {
            1: Position(x_pos=719, y_pos=840),
            2: Position(x_pos=1111, y_pos=519),
            3: Position(x_pos=1197, y_pos=326),
            4: Position(x_pos=1201, y_pos=322),
            5: Position(x_pos=862, y_pos=605),
            6: Position(x_pos=762, y_pos=327),
            7: Position(x_pos=1112, y_pos=346),
            8: Position(x_pos=1287, y_pos=424),
        }
        for folder in os.listdir(PATH_FIXTURES_HIGH):
            img = cv2.imread(os.path.join(PATH_FIXTURES_HIGH, folder, "not.png"))
            high_img = cv2.imread(os.path.join(PATH_FIXTURES_HIGH, folder, "high.png"))
            img = clean_image_after_collect(
                img, high_img, position_by_folder[int(folder)]
            )
            cv2.imshow("i", img)
            cv2.waitKey()

        cv2.waitKey()

import os
import sys
import unittest
from pathlib import Path

import cv2
import numpy

sys.path.append(os.path.join(Path(__file__).parent.parent.parent))


from EzreD2Shared.shared.consts.adaptative.regions import CONTENT_REGION

from src.image_manager.analysis import are_image_similar
from src.image_manager.animation import prepare_img_animation
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_ANIMATION = os.path.join(PATH_FIXTURES, "animation")


class TestAnimation(unittest.TestCase):
    def test_animation_end_fight(self):
        prev_img: numpy.ndarray | None = None

        files_number: list[int] = sorted(
            [int(file[:-4]) for file in os.listdir(PATH_FIXTURES_ANIMATION)]
        )

        img_on_motions: list[int] = []
        for file in files_number:
            img = prepare_img_animation(
                cv2.imread(os.path.join(PATH_FIXTURES_ANIMATION, f"{file}.png")),
                CONTENT_REGION,
            )
            if prev_img is not None and not are_image_similar(prev_img, img):
                img_on_motions.append(file)
            prev_img = img

        assert sorted(img_on_motions) == [6, 7, 8, 9, 10, 11, 12, 13]

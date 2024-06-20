import os
import unittest

import cv2
from backend.src.database import SessionLocal

from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from tests.utils import PATH_FIXTURES


class TestBank(unittest.TestCase):
    def setUp(self):
        self.object_searcher = ObjectSearcher(SessionLocal())

    def test_position_bank_door(self):
        path_img = os.path.join(PATH_FIXTURES, "objects", "bank_door.png")
        img = cv2.imread(path_img)

import os
import unittest
from pathlib import Path

import cv2

from src.bots.dofus.elements.smithmagic_workshop import SmithMagicWorkshop

PATH_FIXTURES = os.path.join(Path(__file__).parent, "fixtures", "history")


class TestParseRunesCount(unittest.TestCase):
    def setUp(self) -> None:
        self.smithmagic_wp = SmithMagicWorkshop()
        return super().setUp()

    def test_same_runes_count(self):
        img1 = cv2.imread(os.path.join(PATH_FIXTURES, "item_runes.png"))
        img2 = cv2.imread(os.path.join(PATH_FIXTURES, "item_runes_same.png"))
        assert self.smithmagic_wp.has_history_changed(img1, img2) is False

    def test_different_runes_count(self):
        img1 = cv2.imread(os.path.join(PATH_FIXTURES, "item_runes.png"))
        img2 = cv2.imread(os.path.join(PATH_FIXTURES, "item_runes-1.png"))
        assert self.smithmagic_wp.has_history_changed(img1, img2) is True

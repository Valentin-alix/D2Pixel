import os
import unittest
from pathlib import Path

import cv2

from src.bots.dofus.elements.smithmagic_workshop import SmithMagicWorkshop
from src.bots.modules.fm.fm_analyser import FmAnalyser
from src.common.loggers.app_logger import AppLogger
from src.gui.signals.app_signals import AppSignals
from src.services.client_service import ClientService

PATH_FIXTURES = os.path.join(Path(__file__).parent, "fixtures", "items")


class TestParseItem(unittest.TestCase):
    def setUp(self) -> None:
        signals = AppSignals()
        logger = AppLogger(signals)
        service = ClientService(logger, signals)
        smithmagic_wp = SmithMagicWorkshop()
        self.fm = FmAnalyser(logger, service, smithmagic_wp)
        return super().setUp()

    def test_forteresse_guerre(self):
        path_img = os.path.join(PATH_FIXTURES, "forteresse_guerre.png")
        img = cv2.imread(path_img)
        stats = self.fm.get_stats_item_selected(img)
        print(stats)
        assert stats is not None and len(stats) == 5
        assert stats[0].value == 2
        assert stats[1].value == 4
        assert stats[2].value == 2
        assert stats[3].value == 15
        assert stats[4].value == -15

    def test_anneau_brouce(self):
        path_img = os.path.join(PATH_FIXTURES, "anneau_brouce.png")
        img = cv2.imread(path_img)
        stats = self.fm.get_stats_item_selected(img)
        assert stats is not None and len(stats) == 10
        assert stats[0].value == 294
        assert stats[1].value == 70
        assert stats[2].value == 26
        assert stats[3].value == 1
        assert stats[4].value == 13
        assert stats[5].value == 11
        assert stats[6].value == 7
        assert stats[7].value == 5
        assert stats[8].value == 6
        assert stats[9].value == 400

    def test_choudini(self):
        path_img = os.path.join(PATH_FIXTURES, "choudini.png")
        img = cv2.imread(path_img)
        stats = self.fm.get_stats_item_selected(img)
        print(stats)
        assert stats is not None and len(stats) == 5
        assert stats[0].value == 3
        assert stats[1].value == 8
        assert stats[2].value == 8
        assert stats[3].value == 6
        assert stats[4].value == -6

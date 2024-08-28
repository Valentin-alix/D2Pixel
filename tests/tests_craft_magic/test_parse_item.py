from logging import Logger
import os
import unittest
from pathlib import Path

import cv2

from D2Shared.shared.schemas.stat import BaseLineSchema
from src.bots.dofus.elements.smithmagic_workshop import SmithMagicWorkshop
from src.bots.modules.fm.fm_analyser import FmAnalyser
from src.gui.signals.app_signals import AppSignals
from src.services.session import ServiceSession


PATH_FIXTURES = os.path.join(Path(__file__).parent, "fixtures", "items")


class TestParseItem(unittest.TestCase):
    def setUp(self) -> None:
        signals = AppSignals()
        logger = Logger("root")
        service = ServiceSession(logger, signals)
        smithmagic_wp = SmithMagicWorkshop()
        self.fm_analyser = FmAnalyser(logger, service, smithmagic_wp)
        return super().setUp()

    def test_forteresse_guerre(self):
        path_img = os.path.join(PATH_FIXTURES, "forteresse_guerre.png")
        img = cv2.imread(path_img)
        lines = self.fm_analyser.get_current_lines_from_img(img)

        print(self.fm_analyser.get_max_lines_values_from_img(img))
        assert lines is not None and len(lines) == 5

        assert lines[0].value == 2
        assert lines[1].value == 4
        assert lines[2].value == 2
        assert lines[3].value == 15
        assert lines[4].value == -15

    def test_anneau_brouce(self):
        path_img = os.path.join(PATH_FIXTURES, "anneau_brouce.png")
        img = cv2.imread(path_img)
        lines = self.fm_analyser.get_current_lines_from_img(img)

        print(self.fm_analyser.get_max_lines_values_from_img(img))
        assert lines is not None and len(lines) == 10

        return

        temp = self.fm_analyser.get_optimal_index_rune_for_target_line(
            10,
            lines[0],
            BaseLineSchema(value=345, stat_id=lines[0].stat_id, stat=lines[0].stat),
        )
        print(temp)

        assert lines[0].value == 294
        assert lines[1].value == 70
        assert lines[2].value == 26
        assert lines[3].value == 1
        assert lines[4].value == 13
        assert lines[5].value == 11
        assert lines[6].value == 7
        assert lines[7].value == 5
        assert lines[8].value == 6
        assert lines[9].value == 400

    def test_choudini(self):
        path_img = os.path.join(PATH_FIXTURES, "choudini.png")
        img = cv2.imread(path_img)
        stats = self.fm_analyser.get_current_lines_from_img(img)
        print(self.fm_analyser.get_max_lines_values_from_img(img))
        assert stats is not None and len(stats) == 5
        assert stats[0].value == 3
        assert stats[1].value == 8
        assert stats[2].value == 8
        assert stats[3].value == 6
        assert stats[4].value == -6

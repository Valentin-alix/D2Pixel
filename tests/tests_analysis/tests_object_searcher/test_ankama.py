import os
import unittest
from logging import Logger

import cv2

from D2Shared.shared.consts.object_configs import ObjectConfigs
from src.gui.signals.app_signals import AppSignals
from src.image_manager.screen_objects.object_searcher import (
    ObjectSearcher,
)
from src.services.session import ServiceSession
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_ANKAMA = os.path.join(PATH_FIXTURES, "ankama")


class TestAnkama(unittest.TestCase):
    def setUp(self):
        logger = Logger("root")
        service = ServiceSession(logger, AppSignals())
        self.object_searcher = ObjectSearcher(logger=logger, service=service)

    def test_ankama_play(self):
        img = cv2.imread(os.path.join(PATH_FIXTURES_ANKAMA, "play.png"))

        pos = self.object_searcher.get_position(img, ObjectConfigs.Ankama.play)
        assert pos is not None

        pos_empty = self.object_searcher.get_position(
            img, ObjectConfigs.Ankama.empty_play
        )
        assert pos_empty is None

    def test_ankama_empty_play(self):
        img = cv2.imread(os.path.join(PATH_FIXTURES_ANKAMA, "empty_play.png"))

        pos = self.object_searcher.get_position(img, ObjectConfigs.Ankama.play)
        assert pos is None

        pos_empty = self.object_searcher.get_position(
            img, ObjectConfigs.Ankama.empty_play
        )
        assert pos_empty is not None

    def test_selected_play(self):
        img = cv2.imread(os.path.join(PATH_FIXTURES_ANKAMA, "selected_play.png"))

        pos = self.object_searcher.get_position(img, ObjectConfigs.Ankama.play)
        assert pos is None

        pos = self.object_searcher.get_position(img, ObjectConfigs.Ankama.empty_play)
        assert pos is None

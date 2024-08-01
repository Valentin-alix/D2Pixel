import os
import unittest
from logging import Logger

import cv2

from D2Shared.shared.consts.object_configs import ObjectConfigs
from src.gui.signals.app_signals import AppSignals
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_FIGHT = os.path.join(PATH_FIXTURES, "fight")


class TestFight(unittest.TestCase):
    def setUp(self):
        logger = Logger("root")
        service = ServiceSession(logger, AppSignals())
        self.object_searcher = ObjectSearcher(logger=logger, service=service)

    def test_in_fight(self):
        path_img = os.path.join(PATH_FIXTURES_FIGHT, "our_turn.png")
        img = cv2.imread(path_img)

        assert (
            self.object_searcher.get_position(img, ObjectConfigs.Fight.in_fight)
            is not None
        )

    def test_out_fight(self):
        path_img = os.path.join(PATH_FIXTURES_FIGHT, "out_fight.png")
        img = cv2.imread(path_img)
        assert (
            self.object_searcher.get_position(img, ObjectConfigs.Fight.in_fight) is None
        )

    def test_choose_chall(self):
        path_img = os.path.join(PATH_FIXTURES_FIGHT, "fight_prep", "2.png")
        img = cv2.imread(path_img)
        assert (
            self.object_searcher.get_position(img, ObjectConfigs.Fight.choose_chall)
            is not None
        )

    def test_ressucite_text(self):
        path_img = os.path.join(PATH_FIXTURES_FIGHT, "ressucite_text.png")
        img = cv2.imread(path_img)
        pos_info = self.object_searcher.get_position(
            img, ObjectConfigs.Fight.ressuscite_text
        )
        assert pos_info is not None

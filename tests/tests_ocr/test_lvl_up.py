import os
import unittest
from logging import Logger

import cv2

from D2Shared.shared.consts.object_configs import ObjectConfigs
from src.bots.dofus.hud.hud_system import Hud
from src.gui.signals.app_signals import AppSignals
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_LVL_UP = os.path.join(PATH_FIXTURES, "hud", "lvl_up")


class TestLvlUp(unittest.TestCase):
    def setUp(self) -> None:
        logger = Logger("root")
        self.hud = Hud(logger=logger)
        service_session = ServiceSession(logger=logger, app_signals=AppSignals())
        self.object_searcher = ObjectSearcher(logger=logger, service=service_session)
        return super().setUp()

    def test_lvl_up(self):
        for filename in os.listdir(PATH_FIXTURES_LVL_UP):
            img = cv2.imread(os.path.join(PATH_FIXTURES_LVL_UP, filename))

            # TODO Omega
            if "omega_" in filename[:-4]:
                expected_lvl_up = 64
            else:
                expected_lvl_up = int(filename[:-4])

            pos, template_found = self.object_searcher.get_position(
                img, ObjectConfigs.Text.level_up, force=True
            )
            new_level = self.hud.get_level_up_number(img, pos, template_found.region)
            print(new_level)
            assert expected_lvl_up == new_level

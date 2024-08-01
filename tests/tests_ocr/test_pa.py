import os
import unittest
from logging import Logger

import cv2

from src.bots.dofus.hud.pa import get_pa
from src.gui.signals.app_signals import AppSignals
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_FIGHT = os.path.join(PATH_FIXTURES, "fight")


class TestInfoModal(unittest.TestCase):
    def setUp(self):
        logger = Logger("root")
        app_signals = AppSignals()
        self.service = ServiceSession(logger=logger, app_signals=app_signals)
        self.object_searcher = ObjectSearcher(logger=logger, service=self.service)

    def test_get_pa(self):
        PA_FIXTURES = os.path.join(PATH_FIXTURES_FIGHT, "pa")

        pa_by_filename: dict[str, int] = {
            "-1_pa": -1,
            "6_pa": 6,
            "7_pa": 7,
            "8_pa": 8,
            "9_pa": 9,
            "10_pa": 10,
            "11_pa": 11,
        }

        for filename in os.listdir(PA_FIXTURES):
            img = cv2.imread(os.path.join(PA_FIXTURES, filename))
            pa = get_pa(img)
            assert pa == pa_by_filename[filename[:-4]]

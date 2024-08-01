import os
import unittest
from logging import Logger

import cv2

from D2Shared.shared.consts.object_configs import ObjectConfigs
from src.bots.dofus.walker.maps import get_bonta_sale_hotel_consumable_map
from src.gui.signals.app_signals import AppSignals
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from tests.utils import PATH_FIXTURES

ZAAPIS_PATH = os.path.join(PATH_FIXTURES, "hud", "zaapis")


class TestZaapi(unittest.TestCase):
    def setUp(self):
        logger = Logger("root")
        self.service = ServiceSession(logger, AppSignals())
        self.object_searcher = ObjectSearcher(logger=logger, service=self.service)

    def test_zaapi_consu(self):
        path_img = os.path.join(ZAAPIS_PATH, "zaapi_consu.png")
        img = cv2.imread(path_img)

        pos = self.object_searcher.get_position(
            img,
            ObjectConfigs.PathFinding.zaapi,
            get_bonta_sale_hotel_consumable_map(self.service).id,
        )
        print(pos)

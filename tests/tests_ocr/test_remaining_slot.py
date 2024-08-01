import os
import unittest
from logging import Logger

import cv2

from src.bots.dofus.elements.sale_hotel import SaleHotel
from src.bots.dofus.hud.hud_system import Hud
from src.gui.signals.app_signals import AppSignals
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_REMAINING_SLOT = os.path.join(PATH_FIXTURES, "hud", "remaining_slots")


class TestRemainingSlot(unittest.TestCase):
    def setUp(self) -> None:
        logger = Logger("root")
        app_signals = AppSignals()
        self.service = ServiceSession(logger=logger, app_signals=app_signals)
        self.object_searcher = ObjectSearcher(logger=logger, service=self.service)
        self.hud = Hud(logger=logger)
        self.sale_hotel = SaleHotel(logger=logger)
        return super().setUp()

    def test_remaining_slot(self):
        for filename in os.listdir(PATH_FIXTURES_REMAINING_SLOT):
            img = cv2.imread(os.path.join(PATH_FIXTURES_REMAINING_SLOT, filename))

            expected_remaining_slot = int(filename[:-4])

            count_remaining_slot = self.sale_hotel.sale_hotel_get_count_remaining_slot(
                img
            )
            print(count_remaining_slot)

            assert expected_remaining_slot == count_remaining_slot

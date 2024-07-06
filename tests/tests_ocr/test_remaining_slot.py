import os
import unittest

import cv2

from src.bots.dofus.elements.sale_hotel import SaleHotel
from src.bots.dofus.hud.hud_system import Hud
from src.gui.signals.bot_signals import BotSignals
from src.window_manager.organizer import WindowInfo
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_REMAINING_SLOT = os.path.join(PATH_FIXTURES, "hud", "remaining_slots")


class TestRemainingSlot(unittest.TestCase):
    def setUp(self) -> None:
        self.hud = Hud(
            window_info=WindowInfo(hwnd=1, name="temp"), bot_signals=BotSignals()
        )
        self.sale_hotel = SaleHotel(bot_signals=BotSignals(), title="temp")
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

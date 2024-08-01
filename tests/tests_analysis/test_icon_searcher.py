import os
import unittest
from logging import Logger

import cv2

from src.gui.signals.app_signals import AppSignals
from src.image_manager.screen_objects.icon_searcher import IconSearcher
from src.services.session import ServiceSession
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_HUD_BANK = os.path.join(PATH_FIXTURES, "hud", "bank")


class TestIconSearcher(unittest.TestCase):
    def setUp(self) -> None:
        logger = Logger("root")
        self.icon_searcher = IconSearcher(
            logger=logger, service=ServiceSession(logger, AppSignals())
        )
        return super().setUp()

    def test_icon_searcher(self):
        img = cv2.imread(os.path.join(PATH_FIXTURES_HUD_BANK, "1.png"))
        for res in [
            "orge",
            "goujon",
            "sauge",
            "ortie",
            "bois de frêne",
            "blé",
            "greuvette",
            "Encre d'Oktapodas",
            "Peau de Larve Bleue",
            "Gant de Martoa",
            "Slip en Cuir Moulant du Garglyphe",
        ]:
            pos = self.icon_searcher.search_icon_item(item, img)
            print(pos)
            assert pos is not None, res

    def test_false_positive_icon_searcher(self):
        img = cv2.imread(os.path.join(PATH_FIXTURES_HUD_BANK, "2.png"))
        for res in ["Défense du sanglier"]:
            item = (
                self.icon_searcher.session.query(Item)
                .filter(func.lower(Item.name) == func.lower(res))
                .one()
            )
            pos = self.icon_searcher.search_icon_item(item, img)
            assert pos is None, res

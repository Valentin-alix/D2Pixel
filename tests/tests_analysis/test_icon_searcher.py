import os
import unittest
from logging import Logger

import cv2

from D2Shared.shared.utils.clean import clean_item_name
from src.gui.signals.app_signals import AppSignals
from src.image_manager.screen_objects.icon_searcher import IconSearcher
from src.services.item import ItemService
from src.services.session import ServiceSession
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_HUD_BANK = os.path.join(PATH_FIXTURES, "hud", "bank")


class TestIconSearcher(unittest.TestCase):
    def setUp(self) -> None:
        logger = Logger("root")
        self.icon_searcher = IconSearcher(
            logger=logger, service=ServiceSession(logger, AppSignals())
        )
        self.service = ServiceSession(logger, AppSignals())
        self.items = ItemService.get_items(self.service)
        return super().setUp()

    def test_icon_searcher(self):
        img = cv2.imread(os.path.join(PATH_FIXTURES_HUD_BANK, "1.png"))

        searched_items = [
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
        ]

        for item in [
            _elem
            for _elem in self.items
            if clean_item_name(_elem.name) in searched_items
            or _elem.name in searched_items
        ]:
            pos = self.icon_searcher.search_icon_item(item, img)
            print(pos)
            assert pos is not None, item

    def test_false_positive_icon_searcher(self):
        img = cv2.imread(os.path.join(PATH_FIXTURES_HUD_BANK, "2.png"))
        searched_items: list[str] = ["Défense du sanglier"]
        for item in [
            _elem
            for _elem in self.items
            if clean_item_name(_elem.name) in searched_items
            or _elem.name in searched_items
        ]:
            pos = self.icon_searcher.search_icon_item(item, img)
            assert pos is None, item

    def test_false_positive_icon_searcher2(self):
        img = cv2.imread(os.path.join(PATH_FIXTURES_HUD_BANK, "1.png"))
        searched_items: list[str] = ["Défense du sanglier", "orge magique"]
        for item in [
            _elem
            for _elem in self.items
            if clean_item_name(_elem.name) in searched_items
            or _elem.name in searched_items
        ]:
            pos = self.icon_searcher.search_icon_item(item, img)
            assert pos is None, item

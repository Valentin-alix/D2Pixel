import os
import unittest

import cv2
from backend.src.database import SessionLocal
from D2Shared.shared.consts.object_configs import ObjectConfigs
from D2Shared.shared.entities.position import Position
from D2Shared.shared.schemas.template_found import TemplateFoundPlacementSchema

from src.image_manager.screen_objects.object_searcher import (
    ObjectSearcher,
)
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_HUD = os.path.join(PATH_FIXTURES, "hud")


class TestHud(unittest.TestCase):
    def setUp(self):
        self.object_searcher = ObjectSearcher(SessionLocal())

    def test_quit_ok_modal(self):
        img = cv2.imread(os.path.join(PATH_FIXTURES_HUD, "modal_ok.png"))
        assert (
            len(
                self.object_searcher.get_multiple_position(
                    img, ObjectConfigs.Cross.bank_inventory_right
                )
            )
            == 0
        )
        assert (
            self.object_searcher.get_position(img, ObjectConfigs.Button.ok) is not None
        )

    def test_cross(self):
        img = cv2.imread(os.path.join(PATH_FIXTURES_HUD, "cross_ok.png"))
        positions: list[tuple[Position, TemplateFoundPlacementSchema]] = []
        for config in [
            ObjectConfigs.Cross.inverted,
            ObjectConfigs.Cross.map,
            ObjectConfigs.Cross.bank_inventory_right,
            ObjectConfigs.Cross.info_win_fight,
        ]:
            positions.extend(self.object_searcher.get_multiple_position(img, config))
        print(positions)

import os
import unittest

import cv2

from src.bots.dofus.hud.hud_system import Hud
from src.data_layer.consts.object_configs import ObjectConfigs
from src.data_layer.schemas.region import RegionSchema
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_LVL_UP = os.path.join(PATH_FIXTURES, "hud", "lvl_up")


class TestLvlUp(unittest.TestCase):
    def setUp(self) -> None:
        self.hud = Hud()
        return super().setUp()

    def test_lvl_up(self):
        for filename in os.listdir(PATH_FIXTURES_LVL_UP):
            img = cv2.imread(os.path.join(PATH_FIXTURES_LVL_UP, filename))

            expected_lvl_up = int(filename[:-4])

            pos, template_found = self.hud.get_position(
                img, ObjectConfigs.Text.level_up, force=True
            )
            new_level = self.hud.get_level_up_number(
                img, pos, RegionSchema.model_validate(template_found.region)
            )
            print(new_level)
            assert expected_lvl_up == new_level

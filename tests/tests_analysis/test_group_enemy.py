import os
import unittest

import cv2

from D2Shared.shared.schemas.region import RegionSchema
from src.bots.dofus.hud.infobulle import iter_infobulles_contours
from src.bots.modules.fighter.fighter import get_group_lvl
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_INFOBUL = os.path.join(PATH_FIXTURES, "infobul")


class TestGroupEnemy(unittest.TestCase):
    def test_area_group(self):
        lvls_by_file: dict[str, list[int]] = {
            "1": [11, 82, 29],
            "2": [76, 30, 96],
            "3": [89, 39, 15],
        }

        for file in os.listdir(PATH_FIXTURES_INFOBUL):
            img = cv2.imread(os.path.join(PATH_FIXTURES_INFOBUL, file))
            target_lvls = sorted(lvls_by_file[file[:-4]])

            lvl_found: list[int] = []
            for _, x, y, width, height in iter_infobulles_contours(img):
                area = RegionSchema(left=x, right=x + width, top=y, bot=y + height)
                if lvl := get_group_lvl(img, area):
                    lvl_found.append(lvl)

            lvl_found = sorted(lvl_found)
            assert (
                target_lvls == lvl_found
            ), f"{target_lvls} != {lvl_found} error for {file}"

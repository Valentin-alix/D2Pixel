import os
import unittest

import cv2

from src.bots.dofus.hud.map import get_map
from src.data_layer.database import SessionLocal
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_MAPS = os.path.join(PATH_FIXTURES, "maps")

PATH_FIXTURES_SPE_MAPS = os.path.join(PATH_FIXTURES, "spe_maps")


class TestOcr(unittest.TestCase):
    def test_all_map(self):
        session = SessionLocal()
        for filename in os.listdir(PATH_FIXTURES_MAPS):
            img = cv2.imread(os.path.join(PATH_FIXTURES_MAPS, filename))
            map = tuple([int(elem) for elem in filename[:-4].split("_")])
            found_map = get_map(session, img)[0]
            assert (
                found_map.x,
                found_map.y,
            ) == map, f"{filename} : {found_map} != {map}"

    def test_spe_map(self):
        session = SessionLocal()
        for filename in os.listdir(PATH_FIXTURES_SPE_MAPS):
            if filename != "-3_-5.png":
                continue
            img = cv2.imread(os.path.join(PATH_FIXTURES_SPE_MAPS, filename))
            map_coords = tuple([int(elem) for elem in filename[:-4].split("_")])
            found_map = get_map(session, img, from_map=None)[0]
            print(found_map)
            assert (
                found_map.x,
                found_map.y,
            ) == map_coords, f"{filename} : {found_map} != {map_coords}"

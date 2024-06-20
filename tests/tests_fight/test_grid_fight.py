import os
import unittest

import cv2

from src.bots.dofus.fight.grid.path_grid import AstarGrid
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_FIGHT = os.path.join(PATH_FIXTURES, "fight")


class TestGridFight(unittest.TestCase):
    def setUp(self) -> None:
        self.grid = AstarGrid()
        return super().setUp()

    def test_grid(self):
        # TODO Test character, enemy, ally, etc..
        SELF_CELLS_FOLDER = os.path.join(PATH_FIXTURES_FIGHT, "turn")

        for filename in os.listdir(SELF_CELLS_FOLDER):
            # if filename != "15.png":
            #     continue
            print(filename)
            img = cv2.imread(os.path.join(SELF_CELLS_FOLDER, filename))

            self.grid.init_grid(img)
            self.grid.parse_grid(img)

            path = self.grid.get_near_movable_to_reach_enemy()
            print(self.grid.enemy_cells)

            self.grid.draw_grid(img)

            self.grid.clear_grid()

            cv2.imshow("i", img)
            cv2.waitKey()

            # break

    def test_grid_prep(self):
        FIGHT_PREP_CELLS_FOLDER = os.path.join(PATH_FIXTURES_FIGHT, "fight_prep")

        for filename in os.listdir(FIGHT_PREP_CELLS_FOLDER):
            print(filename)
            img = cv2.imread(os.path.join(FIGHT_PREP_CELLS_FOLDER, filename))

            self.grid.parse_grid_prep(img)

            path = self.grid.get_near_movable_to_reach_enemy()
            print(path)

            break

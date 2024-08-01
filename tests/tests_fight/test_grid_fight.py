import os
import unittest
from logging import Logger

import cv2

from src.bots.dofus.fight.grid.grid import Grid
from src.bots.dofus.fight.grid.ldv_grid import LdvGrid
from src.bots.dofus.fight.grid.path_grid import AstarGrid
from src.gui.signals.app_signals import AppSignals
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_FIGHT = os.path.join(PATH_FIXTURES, "fight")


class TestGridFight(unittest.TestCase):
    def setUp(self) -> None:
        logger = Logger("root")
        service = ServiceSession(Logger("root"), AppSignals())
        object_searcher = ObjectSearcher(logger, service)
        self.grid = Grid(logger, object_searcher)
        self.astar_grid = AstarGrid(self.grid, logger)
        self.ldv_grid = LdvGrid(self.grid)
        return super().setUp()

    def test_grid(self):
        # TODO Test character, enemy, ally, etc..
        SELF_CELLS_FOLDER = os.path.join(PATH_FIXTURES_FIGHT, "turn")

        for filename in os.listdir(SELF_CELLS_FOLDER):
            img = cv2.imread(os.path.join(SELF_CELLS_FOLDER, filename))

            self.grid.init_grid(img)

            self.grid.parse_grid(img)

            self.grid.draw_grid(img)

            temp_cell = self.astar_grid.get_near_movable_to_reach_enemy()
            print(temp_cell)

            near_mv = self.ldv_grid.get_near_movable_for_ldv_enemy(5)
            print(near_mv)

            self.grid.clear_grid()

    def test_grid_prep(self):
        FIGHT_PREP_CELLS_FOLDER = os.path.join(PATH_FIXTURES_FIGHT, "fight_prep")

        for filename in os.listdir(FIGHT_PREP_CELLS_FOLDER):
            print(filename)
            img = cv2.imread(os.path.join(FIGHT_PREP_CELLS_FOLDER, filename))

            self.grid.parse_grid_prep(img)

            path = self.astar_grid.get_near_movable_to_reach_enemy()
            print(path)

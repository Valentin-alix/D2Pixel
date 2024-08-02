import os
import unittest
from logging import Logger

import cv2

from D2Shared.shared.utils.algos.bresenhman import bresenham_dofus
from src.bots.dofus.fight.grid.grid import Grid
from src.bots.dofus.fight.grid.ldv_grid import LdvGrid

# sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from src.gui.signals.app_signals import AppSignals
from src.image_manager.drawer import ColorBGR, draw_line
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from tests.utils import PATH_FIXTURES


class TestSpellsFight(unittest.TestCase):
    def setUp(self) -> None:
        logger = Logger("root")
        service = ServiceSession(logger=logger, app_signals=AppSignals())
        object_searcher = ObjectSearcher(logger=logger, service=service)
        self.grid = Grid(logger=logger, object_searcher=object_searcher)
        self.ldv_grid = LdvGrid(grid=self.grid)
        return super().setUp()

    def test_get_near_ldv_enemy(self):
        for filename in os.listdir(os.path.join(PATH_FIXTURES, "fight", "turn")):
            img = cv2.imread(os.path.join(PATH_FIXTURES, "fight", "turn", filename))
            self.grid.init_grid(img)
            self.grid.parse_grid(img)
            self.grid.draw_grid(img)

            near_mov_ldv_enemy = self.ldv_grid.get_near_movable_for_ldv_enemy(20)
            if near_mov_ldv_enemy:
                move_cell, enemy_cell = near_mov_ldv_enemy
                draw_line(
                    img,
                    move_cell.center_pos.to_xy(),
                    enemy_cell.center_pos.to_xy(),
                    color=ColorBGR.RED,
                )
            cv2.imshow("img", img)
            cv2.waitKey()

    def test_get_near_no_ldv_enemy(self):
        img = cv2.imread(os.path.join(PATH_FIXTURES, "fight", "turn", "3.png"))

        self.grid.init_grid(img)
        self.grid.parse_grid(img)
        self.grid.draw_grid(img)

        near_mov_ldv_enemy = self.ldv_grid.get_near_movable_for_ldv_enemy(20)
        if near_mov_ldv_enemy:
            move_cell, enemy_cell = near_mov_ldv_enemy
            draw_line(
                img,
                move_cell.center_pos.to_xy(),
                enemy_cell.center_pos.to_xy(),
                color=ColorBGR.RED,
            )
        # print(near_mov_ldv_enemy)
        assert near_mov_ldv_enemy is not None
        curr_cell, target_cell = near_mov_ldv_enemy
        passed = list(
            bresenham_dofus(
                curr_cell.col,
                curr_cell.row,
                target_cell.col,
                target_cell.row,
            )
        )
        print(passed)
        cv2.imshow("img", img)
        cv2.waitKey()

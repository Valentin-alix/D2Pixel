import os
import unittest

import cv2

from src.bots.dofus.fight.grid.ldv_grid import LdvGrid
from src.common.algos.bresenhman import bresenham

# sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from src.gui.signals.bot_signals import BotSignals
from src.image_manager.debug import ColorBGR, draw_line
from src.window_manager.organizer import WindowInfo
from tests.utils import PATH_FIXTURES


class TestSpellsFight(unittest.TestCase):
    def setUp(self) -> None:
        self.ldv_grid = LdvGrid(
            window_info=WindowInfo(hwnd=1, name="temp"), bot_signals=BotSignals()
        )
        return super().setUp()

    def test_get_near_ldv_enemy(self):
        for filename in os.listdir(os.path.join(PATH_FIXTURES, "fight", "turn")):
            img = cv2.imread(os.path.join(PATH_FIXTURES, "fight", "turn", filename))
            self.ldv_grid.init_grid(img)
            self.ldv_grid.parse_grid(img)
            self.ldv_grid.draw_grid(img)

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

        self.ldv_grid.init_grid(img)
        self.ldv_grid.parse_grid(img)
        self.ldv_grid.draw_grid(img)

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
            bresenham(
                curr_cell.col,
                curr_cell.row,
                target_cell.col,
                target_cell.row,
            )
        )
        print(passed)
        cv2.imshow("img", img)
        cv2.waitKey()

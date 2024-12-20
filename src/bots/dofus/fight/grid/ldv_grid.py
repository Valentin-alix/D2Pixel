import random
from dataclasses import dataclass

from D2Shared.shared.enums import TypeCellEnum
from D2Shared.shared.schemas.cell import CellSchema
from D2Shared.shared.utils.algos.bresenhman import bresenham_dofus
from src.bots.dofus.fight.grid.grid import Grid


@dataclass
class LdvGrid:
    grid: Grid

    def get_near_movable_for_ldv_enemy(
        self, max_dist: int
    ) -> tuple[CellSchema, CellSchema] | None:
        assert (curr_cell := self.grid.character_cell) is not None

        near_enemy_with_move_cell: (
            tuple[tuple[CellSchema, CellSchema], tuple[float, float]] | None
        ) = None

        accessible_cell = self.grid.movable_cells.copy()
        if self.grid.character_cell is not None:
            accessible_cell.append(self.grid.character_cell)

        random.shuffle(self.grid.enemy_cells)
        random.shuffle(self.grid.movable_cells)
        for enemy_cell in self.grid.enemy_cells:
            if enemy_cell.get_dist_cell(curr_cell) <= 1:
                return curr_cell, enemy_cell

            for mov_cell in accessible_cell:
                if not self.has_ldv(mov_cell, enemy_cell):
                    continue
                dist_mov_enemy = mov_cell.get_dist_cell(enemy_cell)
                if dist_mov_enemy > max_dist:
                    continue
                dist_mov_character = mov_cell.get_dist_cell(curr_cell)
                if near_enemy_with_move_cell is None or (
                    near_enemy_with_move_cell[1][0] > dist_mov_enemy
                    or (
                        near_enemy_with_move_cell[1][0] == dist_mov_enemy
                        and near_enemy_with_move_cell[1][1] > dist_mov_character
                    )
                ):
                    near_enemy_with_move_cell = (
                        (mov_cell, enemy_cell),
                        (dist_mov_enemy, dist_mov_character),
                    )

        return (
            near_enemy_with_move_cell[0]
            if near_enemy_with_move_cell is not None
            else None
        )

    def has_ldv(self, curr_cell: CellSchema, target_cell: CellSchema) -> bool:
        passed_coord = list(
            bresenham_dofus(
                curr_cell.col,
                curr_cell.row,
                target_cell.col,
                target_cell.row,
            )
        )[1:-1]

        for col, line in passed_coord:
            if self.grid.cells[(col, line)].type_cell in [
                TypeCellEnum.OCCUPED,
                TypeCellEnum.OPAQUE,
            ]:
                return False
        return True

from logging import Logger

from D2Shared.shared.schemas.cell import CellSchema
from D2Shared.shared.utils.algos.astar import find_path
from D2Shared.shared.utils.debugger import timeit
from D2Shared.shared.utils.randomizer import multiply_offset
from src.bots.dofus.fight.grid.grid import Grid


def get_dist_cell_to_multiple_cells(
    current: CellSchema, ends: set[CellSchema]
) -> float:
    return min(current.get_dist_cell(end) for end in ends) * multiply_offset()


class AstarGrid:
    def __init__(self, grid: Grid, logger: Logger) -> None:
        self.grid = grid
        self.logger = logger

    @timeit
    def get_near_movable_to_reach_enemy(
        self, target_cell: CellSchema | None = None
    ) -> CellSchema | None:
        target_cells: list[CellSchema] = (
            [target_cell] if target_cell is not None else self.grid.enemy_cells
        )

        if len(target_cells) == 0:
            return None

        if (curr_cell := self.grid.character_cell) is not None:
            path_to_enemy: list[CellSchema] | None = None
            for cell in sorted(
                target_cells, key=lambda cell: cell.get_dist_cell(curr_cell)
            ):
                if cell.get_dist_cell(curr_cell) <= 1:
                    return None
                path_to_enemy = find_path(
                    curr_cell,
                    set(self.grid.get_neighbors_movable_cell(cell)),
                    get_neighbors_func=self.grid.get_neighbors_movable_cell,
                    distance_between_func=get_dist_cell_to_multiple_cells,
                    do_reverse=True,
                )
                if path_to_enemy is None:
                    continue

                near_cell = next(
                    (cell for cell in path_to_enemy if cell in self.grid.movable_cells),
                    None,
                )
                if near_cell:
                    return near_cell

        self.logger.info("No character cell or path found, find based on movable cell")
        near_cell = min(
            self.grid.movable_cells,
            key=lambda mov_cell: min(
                (_cell.get_dist_cell(mov_cell) for _cell in target_cells),
                default=float("inf"),
            ),
            default=None,
        )
        return near_cell

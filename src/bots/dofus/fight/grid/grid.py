from typing import Iterator

import cv2
import numpy
from EzreD2Shared.shared.consts.adaptative.consts import (
    GRID_CELL_ENEMY_OFFSET_TOP,
    GRID_CELL_HEIGHT,
    GRID_CELL_WIDTH,
    GRID_START_X,
    GRID_START_Y,
)
from EzreD2Shared.shared.consts.object_configs import ObjectConfigs
from EzreD2Shared.shared.entities.position import Position
from EzreD2Shared.shared.utils.debugger import timeit

from src.bots.dofus.dofus_bot import DofusBot
from src.bots.dofus.fight.grid.cell import Cell, TypeCellEnum
from src.image_manager.analysis import is_color_in_range
from src.image_manager.debug import ColorBGR, draw_form, draw_text
from src.image_manager.transformation import crop_image

COUNT_WIDTH_CELL = 14
COUNT_HEIHT_CELL = 20

COLOR_SELF_CELL = [
    (numpy.array([55, 120, 80]), numpy.array([65, 125, 95])),
    (numpy.array([0, 0, 255]), numpy.array([0, 0, 255])),
]
RANGES_COLOR_VOID_CELL: list[tuple[numpy.ndarray, numpy.ndarray]] = [
    (numpy.array([0, 0, 0]), numpy.array([10, 10, 10]))
]
RANGES_COLOR_BLOCK_CELL: list[tuple[numpy.ndarray, numpy.ndarray]] = [
    (numpy.array([55, 80, 85]), numpy.array([61, 86, 91]))
]
RANGES_COLOR_MOVABLE_CELL: list[tuple[numpy.ndarray, numpy.ndarray]] = [
    (numpy.array([40, 105, 70]), numpy.array([78, 140, 107]))
]
RANGES_COLOR_MOVABLE_PREP_CELL: list[tuple[numpy.ndarray, numpy.ndarray]] = [
    (numpy.array([0, 30, 210]), numpy.array([15, 45, 230]))
]


@timeit
def get_base_cells() -> dict[tuple[int, int], Cell]:
    def get_default_neighbor_col_line(col: int, line: int) -> list[tuple[int, int]]:
        return [(col, line + 1), (col, line - 1), (col + 1, line), (col - 1, line)]

    cells_by_xy: dict[tuple[int, int], Cell] = {}

    for line in range(COUNT_HEIHT_CELL):
        for col in range(COUNT_WIDTH_CELL):
            coord = (line + col, line - col)

            cell_pair_pos = Position(
                x_pos=int(col * GRID_CELL_WIDTH + GRID_CELL_WIDTH // 2 + GRID_START_X),
                y_pos=int(
                    line * GRID_CELL_HEIGHT + GRID_CELL_HEIGHT // 2 + GRID_START_Y
                ),
            )
            cells_by_xy[(coord[0], coord[1])] = Cell(
                col=coord[0], line=coord[1], center_pos=cell_pair_pos
            )

            cell_impair_pos = Position(
                x_pos=int(col * GRID_CELL_WIDTH + GRID_CELL_WIDTH + GRID_START_X),
                y_pos=int(line * GRID_CELL_HEIGHT + GRID_CELL_HEIGHT) + GRID_START_Y,
            )
            cells_by_xy[(coord[0] + 1, coord[1])] = Cell(
                col=coord[0] + 1, line=coord[1], center_pos=cell_impair_pos
            )

    for cell in cells_by_xy.values():
        for col, line in get_default_neighbor_col_line(cell.col, cell.line):
            if (related_cell := cells_by_xy.get((col, line))) is not None:
                cell._neighbors.append(related_cell)

    return cells_by_xy


class Grid(DofusBot):
    character_cell: Cell | None
    enemy_cells: list[Cell]
    ally_cells: list[Cell]
    movable_cells: list[Cell]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cells: dict[tuple[int, int], Cell] | None = None
        self.character_cell = None
        self.enemy_cells = []
        self.ally_cells = []
        self.movable_cells = []

    @property
    def cells(self):
        # for lazy loading
        if self._cells is None:
            self._cells = get_base_cells()
        return self._cells

    def clear_grid(self):
        self.enemy_cells.clear()
        self.ally_cells.clear()
        self.movable_cells.clear()

    def init_grid(self, img: numpy.ndarray):
        """init grid at starting fight, check void and block cells

        Args:
            img (numpy.ndarray)
        """
        self.clear_grid()
        self.character_cell = None

        for cell in self.cells.values():
            cell_top_img = crop_image(img, cell.region_top)
            average_cell_color = numpy.array(cv2.mean(cell_top_img))[:-1]
            if self._is_void_cell(average_cell_color):
                cell.type_cell = TypeCellEnum.VOID
                continue
            if self._is_block_cell(average_cell_color):
                cell.type_cell = TypeCellEnum.OPAQUE
                continue
            cell.type_cell = TypeCellEnum.NORMAL

    @timeit
    def parse_grid_prep(self, img: numpy.ndarray):
        """parse grid at fight preparation

        Args:
            img (numpy.ndarray)
        """
        for cell in self.cells.values():
            if cell.type_cell in [TypeCellEnum.VOID, TypeCellEnum.OPAQUE]:
                continue
            cell_top_img = crop_image(img, cell.region_top)
            average_cell_color = numpy.array(cv2.mean(cell_top_img))[:-1]
            if self._is_movable_prep_cell(average_cell_color):
                cell.type_cell = TypeCellEnum.NORMAL
                self.movable_cells.append(cell)
                continue
            if self._is_enemy_cell(cell, img):
                self.enemy_cells.append(cell)
                cell.type_cell = TypeCellEnum.OCCUPED
                continue
            cell.type_cell = TypeCellEnum.NORMAL

    @timeit
    def parse_grid(
        self, img: numpy.ndarray, expected_character_cell: Cell | None = None
    ) -> None:
        """refresh allies cell, enemy cell, need to be in fight (not in fight prep)"""
        self.clear_grid()

        did_found_character: bool = False
        for cell in self.cells.values():
            if cell.type_cell in [TypeCellEnum.VOID, TypeCellEnum.OPAQUE]:
                continue
            cell_img = crop_image(img, cell.get_region())
            if self._is_ally_cell(cell_img):
                cell.type_cell = TypeCellEnum.OCCUPED
                if self._is_character_cell(cell_img):
                    self.character_cell = cell
                    did_found_character = True
                else:
                    self.ally_cells.append(cell)
                continue

            cell_top_img = crop_image(img, cell.region_top)
            average_cell_color = numpy.array(cv2.mean(cell_top_img))[:-1]
            if self._is_movable_cell(average_cell_color):
                cell.type_cell = TypeCellEnum.NORMAL
                self.movable_cells.append(cell)
                continue
            if self._is_enemy_cell(cell, img):
                cell.type_cell = TypeCellEnum.OCCUPED
                self.enemy_cells.append(cell)
                continue
            cell.type_cell = TypeCellEnum.NORMAL

        if not did_found_character and len(self.ally_cells) > 0:
            # guess character cell based on allies cells found
            if not expected_character_cell:
                expected_character_cell = self.character_cell

            if expected_character_cell is not None:
                self.character_cell = min(
                    self.ally_cells,
                    key=lambda cell: cell.get_dist_cell(expected_character_cell),
                )
            else:
                self.character_cell = self.ally_cells[0]

            self.ally_cells.remove(self.character_cell)

    def _is_ally_cell(self, cell_img: numpy.ndarray) -> bool:
        mask_red = cv2.inRange(cell_img, *COLOR_SELF_CELL[1])
        return cv2.countNonZero(mask_red) > 5

    def _is_character_cell(self, cell_img: numpy.ndarray) -> bool:
        mask_green = cv2.inRange(cell_img, *COLOR_SELF_CELL[0])
        return cv2.countNonZero(mask_green) > 5

    def _is_enemy_cell(self, cell: Cell, img: numpy.ndarray) -> bool:
        cell_img = crop_image(img, cell.get_region((5, 5, 25, 5)))
        return (
            self.get_position(cell_img, ObjectConfigs.Fight.enemy, with_crop=False)
            is not None
        )

    def _is_void_cell(self, average_cell_color: numpy.ndarray) -> bool:
        return any(
            is_color_in_range(average_cell_color, range_color)
            for range_color in RANGES_COLOR_VOID_CELL
        )

    def _is_block_cell(self, average_cell_color: numpy.ndarray) -> bool:
        return any(
            is_color_in_range(average_cell_color, range_color)
            for range_color in RANGES_COLOR_BLOCK_CELL
        )

    def _is_movable_cell(self, average_cell_color: numpy.ndarray) -> bool:
        return any(
            is_color_in_range(average_cell_color, range_color)
            for range_color in RANGES_COLOR_MOVABLE_CELL
        )

    def _is_movable_prep_cell(self, average_cell_color: numpy.ndarray) -> bool:
        return any(
            is_color_in_range(average_cell_color, range_color)
            for range_color in RANGES_COLOR_MOVABLE_PREP_CELL
        )

    def get_col_line_by_pos(self, pos: Position) -> tuple[int, int]:
        _pos = Position(
            x_pos=int(pos.x_pos - GRID_START_X), y_pos=pos.y_pos - GRID_START_Y
        )

        n_col = _pos.x_pos / GRID_CELL_WIDTH - 1
        n_line = _pos.y_pos / GRID_CELL_HEIGHT - 1

        n_col = round(n_col * 2) / 2
        n_line = round(n_line * 2) / 2

        col, line = int(n_line + n_col + 1), int(n_line - n_col)

        return col, line

    def get_neighbors_movable_cell(self, curr_cell: Cell) -> Iterator[Cell]:
        return (
            cell
            for cell in curr_cell.neighbors
            if cell.type_cell in [TypeCellEnum.NORMAL, TypeCellEnum.UNKNOWN]
        )

    def get_cell_enemy_by_pos(self, enemy_pos: Position) -> Cell:
        offset_pos = Position(
            x_pos=enemy_pos.x_pos, y_pos=enemy_pos.y_pos + GRID_CELL_ENEMY_OFFSET_TOP
        )
        return self.cells[self.get_col_line_by_pos(offset_pos)]

    def draw_grid(self, img: numpy.ndarray):
        for cell in self.cells.values():
            color = ColorBGR.GREEN
            match cell.type_cell:
                case TypeCellEnum.OCCUPED:
                    color = ColorBGR.RED
                case TypeCellEnum.VOID:
                    color = ColorBGR.WHITE
                case TypeCellEnum.OPAQUE:
                    color = ColorBGR.BLUE
                case TypeCellEnum.UNKNOWN:
                    color = ColorBGR.BLACK
            # draw_area(img, cell.get_area((5, 5, 25, 5)), color)
            draw_form(img, cell.points, color)

            draw_text(
                img,
                text=f"{cell.col}:{cell.line}",
                position=Position(
                    x_pos=cell.center_pos.x_pos - 15, y_pos=cell.center_pos.y_pos
                ),
                color=ColorBGR.WHITE,
                thickness=1,
            )

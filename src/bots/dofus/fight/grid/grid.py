from dataclasses import dataclass, field
from logging import Logger
from typing import Iterator

import cv2
import numpy

from D2Shared.shared.consts.adaptative.consts import (
    GRID_CELL_HEIGHT,
    GRID_CELL_WIDTH,
    GRID_START_X,
    GRID_START_Y,
)
from D2Shared.shared.consts.object_configs import ObjectConfigs
from D2Shared.shared.entities.position import Position
from D2Shared.shared.enums import TypeCellEnum
from D2Shared.shared.schemas.cell import CellSchema
from D2Shared.shared.utils.debugger import timeit
from src.image_manager.analysis import is_color_in_range
from src.image_manager.drawer import ColorBGR, draw_form, draw_text
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.image_manager.transformation import crop_image

COUNT_WIDTH_CELL = 14
COUNT_HEIHT_CELL = 40

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
def get_base_cells() -> dict[tuple[int, int], CellSchema]:
    def get_default_neighbor_col_row(col: int, row: int) -> list[tuple[int, int]]:
        if (row % 2) == 0:
            return [
                (col, row - 1),
                (col - 1, row - 1),
                (col - 1, row + 1),
                (col, row + 1),
            ]
        else:
            return [
                (col + 1, row - 1),
                (col, row - 1),
                (col, row + 1),
                (col + 1, row + 1),
            ]

    cells_by_xy: dict[tuple[int, int], CellSchema] = {}

    start_grid_x = GRID_START_X + GRID_CELL_WIDTH // 2
    start_grid_y = GRID_START_Y + GRID_CELL_HEIGHT // 2

    for row in range(COUNT_HEIHT_CELL):
        for col in range(COUNT_WIDTH_CELL):
            cell_x = (
                col * GRID_CELL_WIDTH + (row % 2) * (GRID_CELL_WIDTH / 2) + start_grid_x
            )
            cell_y = (row * GRID_CELL_HEIGHT / 2) + 0 + start_grid_y

            cell_pos = Position(x_pos=int(cell_x), y_pos=int(cell_y))
            cells_by_xy[(col, row)] = CellSchema(col=col, row=row, center_pos=cell_pos)

    for cell in cells_by_xy.values():
        for col, row in get_default_neighbor_col_row(cell.col, cell.row):
            if (related_cell := cells_by_xy.get((col, row))) is not None:
                cell._neighbors.append(related_cell)

    return cells_by_xy


@dataclass
class Grid:
    logger: Logger
    object_searcher: ObjectSearcher

    _cells: dict[tuple[int, int], CellSchema] | None = field(default=None, init=False)
    character_cell: CellSchema | None = field(default=None, init=False)
    enemy_cells: list[CellSchema] = field(default_factory=lambda: [], init=False)
    ally_cells: list[CellSchema] = field(default_factory=lambda: [], init=False)
    movable_cells: list[CellSchema] = field(default_factory=lambda: [], init=False)

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
        self.logger.info("Parsing grid at preparation")
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
        self, img: numpy.ndarray, expected_character_cell: CellSchema | None = None
    ) -> None:
        """refresh allies cell, enemy cell, need to be in fight (not in fight prep)"""
        self.clear_grid()

        self.logger.info("Parsing grid")
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

    def _is_enemy_cell(self, cell: CellSchema, img: numpy.ndarray) -> bool:
        cell_img = crop_image(img, cell.get_region((5, 5, 25, 5)))
        return (
            self.object_searcher.get_position(
                cell_img, ObjectConfigs.Fight.enemy, use_cache=False
            )
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

    def get_neighbors_movable_cell(self, curr_cell: CellSchema) -> Iterator[CellSchema]:
        return (
            cell
            for cell in curr_cell.neighbors
            if cell.type_cell in [TypeCellEnum.NORMAL, TypeCellEnum.UNKNOWN]
        )

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
                text=f"{cell.row}:{cell.col}",
                position=Position(
                    x_pos=cell.center_pos.x_pos - 15, y_pos=cell.center_pos.y_pos
                ),
                color=ColorBGR.WHITE,
                thickness=1,
            )

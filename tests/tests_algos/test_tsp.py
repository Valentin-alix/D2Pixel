import unittest
from time import perf_counter
from typing import TypedDict

import numpy

from D2Shared.shared.entities.position import Position
from src.bots.modules.harvester.path_positions import (
    find_optimal_path_positions,
)
from src.image_manager.drawer import ColorBGR, draw_line, draw_position


def draw_paths(
    img: numpy.ndarray,
    positions: list[Position],
    start_pos: Position,
    end_pos: Position,
):
    for index, pos in enumerate(positions):
        start = (
            (positions[index - 1].x_pos, positions[index - 1].y_pos)
            if index > 0
            else (start_pos.x_pos, start_pos.y_pos)
        )
        draw_line(img, start, (pos.x_pos, pos.y_pos))

    draw_line(
        img, (positions[-1].x_pos, positions[-1].y_pos), (end_pos.x_pos, end_pos.y_pos)
    )


class PositionInfos(TypedDict):
    start: Position
    end: Position
    intermediate: list[Position]
    max_dist: float


class TestHarvestPaths(unittest.TestCase):
    def test_optimal_path(self):
        POSITIONS_INFOS: list[PositionInfos] = [
            PositionInfos(
                start=Position(x_pos=20, y_pos=20),
                end=Position(x_pos=1000, y_pos=900),
                intermediate=[
                    Position(x_pos=500, y_pos=300),
                    Position(x_pos=20, y_pos=800),
                    Position(x_pos=100, y_pos=200),
                    Position(x_pos=340, y_pos=750),
                    Position(x_pos=800, y_pos=900),
                    Position(x_pos=400, y_pos=600),
                    Position(x_pos=420, y_pos=100),
                    Position(x_pos=340, y_pos=20),
                    Position(x_pos=700, y_pos=300),
                    Position(x_pos=38, y_pos=800),
                    Position(x_pos=38, y_pos=800),
                ],
                max_dist=4100,
            ),
            PositionInfos(
                start=Position(x_pos=20, y_pos=20),
                end=Position(x_pos=1000, y_pos=900),
                intermediate=[
                    Position(x_pos=500, y_pos=300),
                    Position(x_pos=20, y_pos=800),
                    Position(x_pos=420, y_pos=100),
                    Position(x_pos=340, y_pos=20),
                    Position(x_pos=700, y_pos=300),
                    Position(x_pos=38, y_pos=840),
                    Position(x_pos=784, y_pos=800),
                    Position(x_pos=746, y_pos=700),
                    Position(x_pos=120, y_pos=670),
                    Position(x_pos=531, y_pos=51),
                    Position(x_pos=340, y_pos=78),
                    Position(x_pos=463, y_pos=32),
                    Position(x_pos=463, y_pos=900),
                ],
                max_dist=4100,
            ),
        ]

        for pos_info in POSITIONS_INFOS:
            img = numpy.zeros((1920, 1009, 3), dtype=numpy.uint8)
            for pos in pos_info["intermediate"]:
                draw_position(img, pos, ColorBGR.WHITE)
            draw_position(img, pos_info["start"], ColorBGR.RED)
            draw_position(img, pos_info["end"], ColorBGR.RED)

            before = perf_counter()

            total_dist, optimal_path = find_optimal_path_positions(
                pos_info["intermediate"], pos_info["start"], pos_info["end"]
            )

            time_spent = perf_counter() - before

            # cv2.imshow("image", img)
            # cv2.waitKey()

            assert time_spent < 1

            assert total_dist < pos_info["max_dist"]

            draw_paths(img, optimal_path, pos_info["start"], pos_info["end"])

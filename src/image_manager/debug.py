from typing import Any

import cv2

import numpy
from cv2.typing import MatLike
from EzreD2Shared.shared.entities.position import Position
from EzreD2Shared.shared.schemas.map import MapSchema
from EzreD2Shared.shared.schemas.region import RegionSchema


class ColorBGR:
    RED = (0, 0, 255)
    BLUE = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (0, 255, 255)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)


def draw_text(
    img: numpy.ndarray,
    text: Any,
    color: tuple[int, int, int] = ColorBGR.RED,
    position: Position | None = None,
    thickness: int = 2,
    font_scale: float = 0.5,
) -> None:
    height, width = img.shape[:2]

    pos_text: tuple[int, int] = (
        (width // 2, height // 2)
        if position is None
        else (position.x_pos, position.y_pos)
    )

    cv2.putText(
        img=img,
        text=str(text),
        org=pos_text,
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=font_scale,
        color=color,
        thickness=thickness,
        lineType=2,
    )


def draw_position(
    img: numpy.ndarray,
    position: Position,
    color: tuple[int, int, int] = ColorBGR.GREEN,
    thickness: int = 1,
    axes=(3, 3),
):
    cv2.ellipse(
        img=img,
        center=(position.x_pos, position.y_pos),
        axes=axes,
        angle=0,
        startAngle=0,
        endAngle=360,
        color=color,
        thickness=thickness,
    )


def draw_area(
    img: numpy.ndarray,
    area: RegionSchema,
    color: tuple[int, int, int] = ColorBGR.GREEN,
    thickness: int = 2,
):
    cv2.rectangle(
        img=img,
        pt1=(area.left, area.top),
        pt2=(area.right, area.bot),
        color=color,
        thickness=thickness,
    )


def draw_contour(
    img: numpy.ndarray,
    contour: MatLike,
    color: tuple[int, int, int] = ColorBGR.GREEN,
    thickness: int = 3,
):
    cv2.drawContours(img, [contour], -1, color, thickness)


def draw_line(
    img: numpy.ndarray,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int] = ColorBGR.GREEN,
    thickness: int = 5,
):
    cv2.line(
        img,
        start,
        end,
        color,
        thickness,
    )


def draw_form(
    img: numpy.ndarray,
    points: numpy.ndarray,
    color: tuple[int, int, int] = ColorBGR.GREEN,
):
    cv2.polylines(img, [points], True, color, thickness=3)


def draw_maps_on_grid(maps: list[MapSchema]):
    import matplotlib.pyplot as plt

    maps_x = [map.x for map in maps]
    maps_y = [map.y for map in maps]

    plt.scatter(maps_x, maps_y, color="black", marker="o")

    min_x = min(maps_x)
    min_y = min(maps_y)

    max_x = max(maps_x)
    max_y = max(maps_y)

    print(min_x, min_y, max_x)

    plt.xlim(-37, -17)
    plt.ylim(-66, -45)

    plt.xlabel("Axe X")
    plt.ylabel("Axe Y")

    plt.gca().invert_yaxis()

    plt.grid(True)
    plt.show()

from typing import Iterator

import cv2
import numpy
from cv2.typing import MatLike
from EzreD2Shared.shared.entities.position import Position
from EzreD2Shared.shared.schemas.region import RegionSchema


def are_same_image(image1: numpy.ndarray, image2: numpy.ndarray) -> bool:
    return image1.shape == image2.shape and not (
        numpy.bitwise_xor(image1, image2).any()
    )


def are_image_similar(
    image1: numpy.ndarray, image2: numpy.ndarray, threshold=0.05
) -> bool:
    assert 0 <= threshold <= 1
    result: float = numpy.mean((image1 - image2) ** 2)  # type: ignore
    return result <= threshold


def contour_is_square(contour: MatLike, width: int, height: int) -> bool:
    if not contour_has_four_side(contour):
        return False
    ratio = width / height
    return ratio >= 0.9 and ratio <= 1.1


def contour_has_four_side(contour: MatLike) -> bool:
    approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
    return len(approx) == 4


def is_valid_uniform_color_range(
    img: numpy.ndarray,
    color_ranges: list[tuple[numpy.ndarray, numpy.ndarray]],
    min_ratio: float = 0.7,
) -> bool:
    height, width = img.shape[:2]
    masked = numpy.zeros((height, width), dtype=numpy.uint8)
    for min_color, max_color in color_ranges:
        mask_color = cv2.inRange(img, min_color, max_color)
        masked = cv2.bitwise_or(masked, mask_color)

    total_white: int = cv2.countNonZero(masked)
    ratio: float = total_white / (width * height)
    return ratio > min_ratio


def contour_is_valid_ratio(
    max_ratio: float,
    mask: numpy.ndarray,
    x: int,
    y: int,
    width: int,
    height: int,
    min_ratio: float = 0,
) -> bool:
    """check if contour has uniform color (exemple : not empty hole inside) based on ratio"""
    total_white: int = cv2.countNonZero(mask[y : y + height, x : x + width])
    ratio: float = total_white / (width * height)
    return min_ratio <= ratio <= max_ratio


def get_contour_distance_pos(contour: MatLike, pos: Position) -> float:
    return cv2.pointPolygonTest(contour, pos.to_xy(), True)


def iter_position_template_in_image(
    img: numpy.ndarray,
    template: numpy.ndarray,
    threshold: float = 0.85,
    method=cv2.TM_CCOEFF_NORMED,
    offset_area: RegionSchema | None = None,
    mask: numpy.ndarray | None = None,
) -> Iterator[Position]:
    height_template, width_template = template.shape[:2]

    result = cv2.matchTemplate(img, template, method, mask=mask)

    max_val: float = 1
    while max_val > threshold:
        _, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val > threshold:
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                x, y = min_loc
            else:
                x, y = max_loc

            x_pos, y_pos = x + width_template // 2, y + height_template // 2
            if offset_area is not None:
                x_pos += offset_area.left
                y_pos += offset_area.top
            yield Position(x_pos=x_pos, y_pos=y_pos)
            result[
                max(y - height_template // 2, 0) : y + height_template // 2 + 1,
                max(x - width_template // 2, 0) : x + width_template // 2 + 1,
            ] = 0


def get_multiple_position_template_in_image(
    img: numpy.ndarray,
    template: numpy.ndarray,
    threshold: float = 0.85,
    method=cv2.TM_CCOEFF_NORMED,
    offset_area: RegionSchema | None = None,
    mask: numpy.ndarray | None = None,
) -> list[Position]:
    return list(
        iter_position_template_in_image(
            img, template, threshold, method, offset_area, mask
        )
    )


def get_position_template_in_image(
    img: numpy.ndarray,
    template: numpy.ndarray,
    threshold: float = 0.85,
    offset_area: RegionSchema | None = None,
    mask: numpy.ndarray | None = None,
    method: int = cv2.TM_CCOEFF_NORMED,
) -> Position | None:
    return next(
        (
            iter_position_template_in_image(
                img, template, threshold, method, offset_area, mask
            )
        ),
        None,
    )


def is_color_in_range(
    color: numpy.ndarray, range_color: tuple[numpy.ndarray, numpy.ndarray]
) -> bool:
    return bool(((range_color[0] <= color) & (color <= range_color[1])).all())

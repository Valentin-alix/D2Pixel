from typing import Iterator

import cv2
import numpy
from cv2.typing import MatLike
from EzreD2Shared.shared.entities.position import Position

from src.image_manager.analysis import (
    contour_has_four_side,
    get_contour_distance_pos,
)
from src.image_manager.masks import get_black_masked
from src.image_manager.transformation import (
    img_to_gray,
)


def iter_infobulles_contours(
    img: numpy.ndarray,
) -> Iterator[tuple[MatLike, int, int, int, int]]:
    """get infobulles on img"""
    img_masked = get_black_masked(img)

    img_gray = img_to_gray(img_masked)

    contours, _ = cv2.findContours(img_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for contour in contours:
        x, y, width, height = cv2.boundingRect(contour)
        if height < 40 or width < 80:
            continue

        if not contour_has_four_side(contour):
            continue

        yield contour, x, y, width, height


def replace_infobulle(
    no_bul_img: numpy.ndarray, bul_img: numpy.ndarray, pos: Position | None = None
):
    """Replace area where infobulle found in bul_img by same area in no_bul_img near pos"""
    for contour, x, y, width, height in iter_infobulles_contours(bul_img):
        if pos and get_contour_distance_pos(contour, pos) < -300:
            continue

        bul_img[y - 10 : y + height + 10, x - 10 : x + width + 10] = no_bul_img[
            y - 10 : y + height + 10, x - 10 : x + width + 10
        ]

    return bul_img

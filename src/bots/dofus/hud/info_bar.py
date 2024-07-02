from enum import Enum

import cv2
import numpy
from cv2.typing import MatLike
from D2Shared.shared.consts.adaptative.regions import (
    INFO_BAR_FIGHT_REGION,
    INFO_BAR_REGION,
)

from src.image_manager.analysis import is_color_in_range
from src.image_manager.transformation import (
    crop_image,
)

RANGE_COLORS_FIGHT: list[tuple[numpy.ndarray, numpy.ndarray]] = [
    (numpy.array([4, 170, 210]), numpy.array([40, 230, 255])),
    (numpy.array([60, 80, 200]), numpy.array([90, 110, 255])),
]


def prepare_info_bar_fight(img: numpy.ndarray) -> tuple[numpy.ndarray, bool]:
    lower_grey = numpy.array([17, 23, 23])
    highter_grey = numpy.array([26, 35, 35])

    img = crop_image(img, INFO_BAR_FIGHT_REGION)

    mask = cv2.bitwise_not(cv2.inRange(img, lower_grey, highter_grey))

    average = numpy.array(cv2.mean(img, mask=mask))[:-1]

    is_color_fight = any(
        is_color_in_range(average, range) for range in RANGE_COLORS_FIGHT
    )

    return mask, bool(is_color_fight)


RANGE_COLOR_PODS = (numpy.array([45, 170, 85]), numpy.array([85, 210, 120]))


class BarType(Enum):
    PODS = 1


def prepare_info_bar(
    img: numpy.ndarray, expected_bar_type: BarType | None = None
) -> tuple[numpy.ndarray, bool]:
    grey = numpy.array([28, 28, 28])
    light_grey = numpy.array([52, 52, 52])
    dark_grey = numpy.array([13, 13, 13])
    black = numpy.array([0, 0, 0])

    empty_bar_colors = [grey, light_grey, dark_grey, black]

    img = crop_image(img, INFO_BAR_REGION)

    masked_img: MatLike = cv2.inRange(img, grey, grey)
    for index in range(1, len(empty_bar_colors)):
        masked_img = cv2.bitwise_or(
            masked_img,
            cv2.inRange(img, empty_bar_colors[index], empty_bar_colors[index]),
        )

    is_expected_color: bool = True

    if expected_bar_type is not None:
        average = cv2.mean(img, mask=cv2.bitwise_not(masked_img))
        average_array = numpy.array(average)[:-1]
        match expected_bar_type:
            case BarType.PODS:
                is_expected_color = is_color_in_range(average_array, RANGE_COLOR_PODS)

    return cv2.bitwise_not(masked_img), is_expected_color


def get_percentage_info_bar(img: numpy.ndarray) -> float:
    height, width = img.shape[:2]

    total_pixel = height * width
    count_filled_pixels = cv2.countNonZero(img)

    percentage = count_filled_pixels / total_pixel

    return percentage


def get_percentage_info_bar_normal(
    img: numpy.ndarray, expected_bar_type: BarType | None = None
) -> float:
    img, is_expected_color = prepare_info_bar(img, expected_bar_type)
    if not is_expected_color:
        return 0
    return get_percentage_info_bar(img)


def get_percentage_info_bar_fight(img: numpy.ndarray) -> float:
    img, is_color_fight = prepare_info_bar_fight(img)
    if not is_color_fight:
        return 0
    return get_percentage_info_bar(img)


def is_full_pods(img: numpy.ndarray) -> bool:
    return get_percentage_info_bar_normal(img, BarType.PODS) > 0.95

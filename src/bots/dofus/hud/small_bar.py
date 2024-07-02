from enum import Enum

import cv2
import numpy
from cv2.typing import MatLike
from D2Shared.shared.consts.adaptative.regions import INVENTORY_BAR
from D2Shared.shared.schemas.region import RegionSchema

from src.image_manager.transformation import (
    crop_image,
)

RANGE_COLOR_EMPTY_INVENTORY = (numpy.array([60, 60, 60]), numpy.array([70, 70, 70]))


class InventoryBarType(Enum):
    PODS = 1


def prepare_inventory_bar(
    img: numpy.ndarray, region: RegionSchema = INVENTORY_BAR
) -> numpy.ndarray:
    img = crop_image(img, region)

    masked_img: MatLike = cv2.inRange(
        img, RANGE_COLOR_EMPTY_INVENTORY[0], RANGE_COLOR_EMPTY_INVENTORY[1]
    )

    return cv2.bitwise_not(masked_img)


def get_percentage_inventory_bar(img: numpy.ndarray) -> float:
    height, width = img.shape[:2]

    total_pixel = height * width
    count_filled_pixels = cv2.countNonZero(img)

    percentage = count_filled_pixels / total_pixel

    return percentage


def get_percentage_inventory_bar_normal(img: numpy.ndarray) -> float:
    img = prepare_inventory_bar(img)
    return get_percentage_inventory_bar(img)

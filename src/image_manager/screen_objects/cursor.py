import os
from enum import Enum

from cachetools import cached
import cv2
import numpy

from src.consts import ASSET_FOLDER_PATH

CURSOR_FOLDER = os.path.join(ASSET_FOLDER_PATH, "cursors")


class CursorType(Enum):
    SWORD = 1


@cached(cache={})
def get_cursor_images() -> dict[CursorType, numpy.ndarray]:
    cursor_infos: dict[CursorType, numpy.ndarray] = {}
    for cursor_type in CursorType:
        img = cv2.imread(os.path.join(CURSOR_FOLDER, f"{cursor_type.name.lower()}.png"))
        cursor_infos[cursor_type] = img

    return cursor_infos

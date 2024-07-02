from enum import Enum

import cv2
import numpy
from D2Shared.shared.schemas.region import RegionSchema

from src.image_manager.transformation import crop_image


def clean_info_popup_img(img: numpy.ndarray, area: RegionSchema) -> numpy.ndarray:
    img = crop_image(img, area)
    height, width = img.shape[:2]
    img = cv2.resize(img, (int(width // 0.8), int(height // 0.8)))
    img = cv2.copyMakeBorder(img, 20, 20, 20, 20, cv2.BORDER_REPLICATE)
    return img


class EventInfoPopup(Enum):
    LVL_UP_JOB = 2

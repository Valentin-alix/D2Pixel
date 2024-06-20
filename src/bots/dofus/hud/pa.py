import cv2
import numpy
import tesserocr
from EzreD2Shared.shared.consts.adaptative.regions import PA_REGION
from EzreD2Shared.shared.utils.debugger import timeit

from src.image_manager.masks import get_white_masked
from src.image_manager.ocr import (
    BASE_CONFIG,
    get_text_from_image,
    set_config_for_ocr_number,
)
from src.image_manager.transformation import crop_image


@timeit
def get_pa(img: numpy.ndarray):
    img = crop_image(img, PA_REGION)
    img = ~get_white_masked(img)

    img = cv2.copyMakeBorder(
        img, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=[255, 255, 255]
    )

    with tesserocr.PyTessBaseAPI(**BASE_CONFIG) as tes_api:
        set_config_for_ocr_number(tes_api, white_list="-0123456789")
        text = get_text_from_image(img, tes_api)

    return int(text)

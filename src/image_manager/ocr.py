import os
from pathlib import Path

import numpy
import tesserocr
from PIL import Image as Img

BASE_CONFIG = {
    "path": os.path.join(
        Path(__file__).parent.parent.parent, "resources", "tesseract", "tessdata"
    )
}


def set_config_for_ocr_number(
    tes_api: tesserocr.PyTessBaseAPI, white_list: str = "0123456789"
):
    tes_api.SetPageSegMode(tesserocr.PSM.SINGLE_LINE)
    tes_api.SetVariable("tessedit_char_whitelist", white_list)
    # don't load dictionnary
    tes_api.SetVariable("load_system_dawg", "false")
    tes_api.SetVariable("load_freq_dawg", "false")


def get_text_from_image(
    img: numpy.ndarray,
    tes_api: tesserocr.PyTessBaseAPI | None = None,
    config: dict[str, str] = BASE_CONFIG,
) -> str:
    def get_text_img(api: tesserocr.PyTessBaseAPI):
        pil_img = Img.fromarray(img)
        api.SetImage(pil_img)
        return api.GetUTF8Text()

    if tes_api is None:
        with tesserocr.PyTessBaseAPI(**config) as api:  # type: ignore
            return get_text_img(api)
    else:
        return get_text_img(tes_api)

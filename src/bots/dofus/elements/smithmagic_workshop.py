import numpy
import tesserocr

from D2Shared.shared.consts.adaptative.regions import HISTORY_AREA, MERGE_AREA
from D2Shared.shared.utils.clean import clean_line_text
from src.image_manager.analysis import are_image_similar
from src.image_manager.ocr import BASE_CONFIG
from src.image_manager.transformation import crop_image
from PIL import Image as Img


class SmithMagicWorkshop:
    def has_history_changed(
        self, old_runes_count_img: numpy.ndarray | None, new_image: numpy.ndarray | None
    ) -> bool:
        if old_runes_count_img is None or new_image is None:
            return old_runes_count_img != new_image

        cropped_img = crop_image(new_image, HISTORY_AREA)
        old_cropped_img = crop_image(old_runes_count_img, HISTORY_AREA)

        return not are_image_similar(old_cropped_img, cropped_img)

    def is_on_smithmagic_workshop(self, image: numpy.ndarray) -> bool:
        pil_img = Img.fromarray(image)
        with tesserocr.PyTessBaseAPI(**BASE_CONFIG) as tes_api:
            tes_api.SetImage(pil_img)
            tes_api.SetRectangle(
                MERGE_AREA.left,
                MERGE_AREA.top,
                MERGE_AREA.right - MERGE_AREA.left,
                MERGE_AREA.bot - MERGE_AREA.top,
            )
            text = clean_line_text(tes_api.GetUTF8Text())
        return text == "fusionner"

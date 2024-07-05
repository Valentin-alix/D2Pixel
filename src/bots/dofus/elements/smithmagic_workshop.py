import numpy

from D2Shared.shared.consts.adaptative.regions import HISTORY_AREA
from src.image_manager.analysis import are_image_similar
from src.image_manager.transformation import crop_image


class SmithMagicWorkshop:
    def has_history_changed(
        self, old_runes_count_img: numpy.ndarray | None, new_image: numpy.ndarray | None
    ) -> bool:
        if old_runes_count_img is None or new_image is None:
            return old_runes_count_img != new_image

        cropped_img = crop_image(new_image, HISTORY_AREA)
        old_cropped_img = crop_image(old_runes_count_img, HISTORY_AREA)

        return not are_image_similar(old_cropped_img, cropped_img)

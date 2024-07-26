import re

import cv2
import numpy
import tesserocr
import unidecode
from D2Shared.shared.consts.adaptative.regions import (
    MAP_POSITION_REGION,
    ZONE_TEXT_REGION,
)
from D2Shared.shared.schemas.map import MapSchema

from src.exceptions import UnknowStateException
from src.image_manager.ocr import (
    BASE_CONFIG,
    get_text_from_image,
    set_config_for_ocr_number,
)
from src.image_manager.transformation import crop_image, get_inverted_image
from src.services.map import MapService
from src.services.session import ServiceSession


def get_map(
    service: ServiceSession, img: numpy.ndarray, from_map: MapSchema | None = None
) -> tuple[MapSchema, str]:
    img = get_inverted_image(img)

    zone_text_img = crop_image(img, ZONE_TEXT_REGION)
    map_pos_img = crop_image(img, MAP_POSITION_REGION)

    map_pos_img = cv2.copyMakeBorder(
        map_pos_img, 5, 0, 0, 0, cv2.BORDER_CONSTANT, value=[255, 255, 255]
    )

    height, width = map_pos_img.shape[:2]
    map_pos_img = cv2.resize(map_pos_img, (int(width * 1.5), int(height * 1.5)))

    with tesserocr.PyTessBaseAPI(**BASE_CONFIG) as tes_api:
        tes_api.SetPageSegMode(tesserocr.PSM.SINGLE_LINE)
        zone_text = get_text_from_image(zone_text_img, tes_api)
        set_config_for_ocr_number(tes_api, ",-0123456789")
        pos_text = get_text_from_image(map_pos_img, tes_api).replace("\n", "")

    try:
        hyphen_witout_comma = re.search(r"([0-9 ])-", pos_text)
        if hyphen_witout_comma:
            before_hyphen = hyphen_witout_comma.end() - 1
            pos_text = pos_text[:before_hyphen] + "," + pos_text[before_hyphen:]

        coordinates = [
            "".join(re.findall(r"[0-9-]+", elem)) for elem in pos_text.split(",")
        ]
        zone_text = unidecode.unidecode(zone_text, "utf-8").lower()

        if coordinates[1][0] == "7" and len(coordinates[1]) == 3:
            # fix tesseract misinterpret 7 with hyphen sometimes
            coordinates[1] = "-" + coordinates[1][1:]
    except IndexError:
        raise UnknowStateException(img, f"map_coordinates_{pos_text.replace(" ", "_")}")

    map = MapService.get_map_from_hud(
        service, zone_text, from_map.id if from_map else None, coordinates
    )
    if map is None:
        raise UnknowStateException(
            img, f"related_neighbor_map_{coordinates}_{from_map}"
        )
    return map, zone_text

import os
from dataclasses import dataclass
from logging import Logger

import cv2
import numpy

from D2Shared.shared.consts.adaptative.consts import (
    INVENTORY_CELL_HEIGHT,
    INVENTORY_CELL_OFFSET,
    INVENTORY_CELL_OFFSET_TOP,
    INVENTORY_CELL_WIDTH,
)
from D2Shared.shared.consts.adaptative.regions import LEFT_INVENTORY_REGION
from D2Shared.shared.entities.position import Position
from D2Shared.shared.schemas.item import ItemSchema
from D2Shared.shared.schemas.region import RegionSchema
from src.consts import ASSET_FOLDER_PATH
from src.image_manager.analysis import get_position_template_in_image
from src.image_manager.masks import get_not_brown_masked
from src.image_manager.transformation import crop_image
from src.services.item import ItemService
from src.services.session import ServiceSession

PATH_ICONS = os.path.join(ASSET_FOLDER_PATH, "icons")

STORAGE_COUNT_CELL_X = 5
STORAGE_COUNT_CELL_Y = 10


@dataclass
class IconSearcher:
    logger: Logger
    service: ServiceSession

    def get_icon_item_img(self, item: ItemSchema) -> numpy.ndarray | None:
        img_icon = ItemService.get_icon_img(self.service, item.id)
        if img_icon is None:
            return None
        height, width = img_icon.shape[:2]
        img_icon_cropped = crop_image(
            img_icon,
            RegionSchema(
                left=INVENTORY_CELL_OFFSET,
                right=width - INVENTORY_CELL_OFFSET,
                bot=height - INVENTORY_CELL_OFFSET,
                top=INVENTORY_CELL_OFFSET_TOP,
            ),
        )
        return img_icon_cropped

    def search_icon_item(
        self,
        item: ItemSchema,
        img: numpy.ndarray,
        area: RegionSchema = LEFT_INVENTORY_REGION,
    ) -> Position | None:
        self.logger.debug(f"Searching for icon item {item}")
        icon_img = self.get_icon_item_img(item)
        if icon_img is None:
            return None
        img = crop_image(img, area)
        img = get_not_brown_masked(img)

        for cell_y in range(STORAGE_COUNT_CELL_Y):
            for cell_x in range(STORAGE_COUNT_CELL_X):
                area_cell = RegionSchema(
                    left=cell_x * INVENTORY_CELL_WIDTH,
                    right=INVENTORY_CELL_WIDTH + cell_x * INVENTORY_CELL_WIDTH,
                    top=cell_y * INVENTORY_CELL_HEIGHT,
                    bot=cell_y * INVENTORY_CELL_HEIGHT + INVENTORY_CELL_HEIGHT,
                )
                cell_img = crop_image(img, area_cell)
                offset_area = RegionSchema(
                    left=area.left + area_cell.left,
                    top=area.top + area_cell.top,
                    right=0,
                    bot=0,
                )
                pos = get_position_template_in_image(
                    cell_img,
                    icon_img,
                    threshold=0.9,
                    method=cv2.TM_CCOEFF_NORMED,
                    offset_area=offset_area,
                )
                if pos is not None:
                    return pos
        return None

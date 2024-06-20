import os
import sys
from threading import RLock

import cv2

sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from src.data_layer.consts.adaptative.positions import CHAT_TEXT_POSITION
from src.data_layer.consts.adaptative.regions import MAP_POSITION_REGION
from src.data_layer.entities.position import Position
from src.data_layer.schemas.region import RegionSchema
from src.image_manager.debug import ColorBGR, draw_area, draw_position
from src.window_manager.capturer import Capturer
from src.window_manager.organizer import get_windows_by_process_and_name

COLOR_REGION = ColorBGR.GREEN


def show_position_area(areas: list[RegionSchema] = [], positions: list[Position] = []):
    """Used for get the position of the area needed, after img has been saved, go to paint and get position"""
    for window_info in get_windows_by_process_and_name(target_process_name="Dofus.exe"):
        img = Capturer(
            window_info=window_info, focus_lock=RLock(), is_paused=False
        ).capture()
        for area in areas:
            draw_area(img, area, COLOR_REGION)
        for position in positions:
            draw_position(img, position)
    cv2.imshow(
        "positions_areas",
        img,
    )
    cv2.waitKey()


def show_position_area_dofus():
    areas = [MAP_POSITION_REGION]
    positions = [CHAT_TEXT_POSITION]
    show_position_area(areas=areas, positions=positions)


if __name__ == "__main__":
    show_position_area_dofus()

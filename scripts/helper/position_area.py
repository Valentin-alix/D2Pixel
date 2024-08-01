import os
import sys
from logging import Logger
from threading import Event, RLock

import cv2

from D2Shared.shared.consts.adaptative.positions import CHAT_TEXT_POSITION
from D2Shared.shared.consts.adaptative.regions import MAP_POSITION_REGION
from src.consts import DOFUS_WINDOW_SIZE

sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))

from D2Shared.shared.entities.position import Position
from D2Shared.shared.schemas.region import RegionSchema
from src.image_manager.debug import ColorBGR, draw_area, draw_position
from src.window_manager.capturer import Capturer
from src.window_manager.organizer import Organizer, get_windows_by_process_and_name

COLOR_REGION = ColorBGR.GREEN


def show_position_area(areas: list[RegionSchema] = [], positions: list[Position] = []):
    """Used for get the position of the area needed, after img has been saved, go to paint and get position"""
    for window_info in get_windows_by_process_and_name(target_process_name="Dofus.exe"):
        is_paused = Event()
        logger = Logger("root")
        organizer = Organizer(
            window_info=window_info,
            is_paused=is_paused,
            target_window_size=DOFUS_WINDOW_SIZE,
            logger=logger,
        )
        capturer = Capturer(
            action_lock=RLock(),
            organizer=organizer,
            is_paused=is_paused,
            window_info=window_info,
            logger=logger,
        )
        img = capturer.capture()
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

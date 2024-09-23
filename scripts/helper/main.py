import ctypes
import logging
import os
import sys
from logging import Logger
from threading import Event, RLock
from time import sleep

sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))

from D2Shared.shared.entities.position import Position
from src.consts import DOFUS_WINDOW_SIZE
from src.window_manager.controller import Controller
from src.window_manager.organizer import Organizer
from src.window_manager.window_searcher import (
    get_dofus_window_infos,
)

user32 = ctypes.windll.user32

if __name__ == "__main__":
    logger = Logger("root")
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    is_paused = Event()
    dofus_win = get_dofus_window_infos()[0]

    organizer = Organizer(
        window_info=dofus_win,
        is_paused_event=is_paused,
        target_window_width_height=DOFUS_WINDOW_SIZE,
        logger=logger,
    )

    control = Controller(
        logger=logger,
        window_info=dofus_win,
        is_paused_event=is_paused,
        organizer=organizer,
        action_lock=RLock(),
    )
    sleep(2)
    control.click(Position(x_pos=578, y_pos=624))

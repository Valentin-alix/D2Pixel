import os
import sys
from logging import Logger
from pathlib import Path
from threading import Event, Lock
from time import sleep
from typing import Iterator

import cv2
import numpy
from pyparsing import RLock

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.consts import ANKAMA_WINDOW_SIZE, DOFUS_WINDOW_SIZE
from src.window_manager.capturer import Capturer
from src.window_manager.organizer import Organizer
from src.window_manager.window_searcher import get_windows_by_process_and_name

os.makedirs(os.path.join(Path(__file__).parent, "output", "captures"), exist_ok=True)


def iter_img(
    target_window_size: tuple[int, int], target_process_name="Dofus.exe"
) -> Iterator[numpy.ndarray]:
    dc_lock = Lock()
    for window_info in get_windows_by_process_and_name(target_process_name):
        is_paused = Event()
        logger = Logger("root")
        organizer = Organizer(
            window_info=window_info,
            is_paused_event=is_paused,
            target_window_width_height=target_window_size,
            logger=logger,
        )
        capturer = Capturer(
            action_lock=RLock(),
            organizer=organizer,
            is_paused_event=is_paused,
            window_info=window_info,
            logger=logger,
            dc_lock=dc_lock,
        )
        yield capturer.capture()


def get_sc_dofus():
    for index, img in enumerate(
        iter_img(DOFUS_WINDOW_SIZE, target_process_name="Dofus.exe")
    ):
        cv2.imwrite(
            os.path.join(
                Path(__file__).parent, "output", "captures", f"dofus_{index}.png"
            ),
            img,
        )


def get_sc_ankama():
    for index, img in enumerate(
        iter_img(ANKAMA_WINDOW_SIZE, target_process_name="Ankama Launcher.exe")
    ):
        cv2.imwrite(
            os.path.join(
                Path(__file__).parent, "output", "captures", f"ankama_{index}.png"
            ),
            img,
        )


if __name__ == "__main__":
    sleep(4)
    get_sc_ankama()

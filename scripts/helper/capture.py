import os
import sys
from pathlib import Path
from typing import Iterator

import cv2
import numpy

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
)

from src.consts import ANKAMA_WINDOW_SIZE, DOFUS_WINDOW_SIZE
from src.window_manager.capturer import Capturer
from src.window_manager.organizer import get_windows_by_process_and_name

os.makedirs(os.path.join(Path(__file__).parent, "output", "captures"), exist_ok=True)


def iter_img(
    target_window_size: tuple[int, int], target_process_name="Dofus.exe"
) -> Iterator[numpy.ndarray]:
    for window_info in get_windows_by_process_and_name(target_process_name):
        capturer = Capturer(
            log_header="temp",
            window_info=window_info,
            target_window_size=target_window_size,
            is_paused=False,
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
    # sleep(4)
    get_sc_dofus()

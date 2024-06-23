import datetime
import os
from pathlib import Path

import cv2
import numpy


class AuthenticationError(Exception): ...


class StoppedException(Exception): ...


class NotPrintableWindow(Exception): ...


class UnknowStateException(Exception):
    def __init__(self, img: numpy.ndarray, msg: str, *args) -> None:
        cv2.imwrite(
            os.path.join(
                Path(__file__).parent.parent,
                "logs",
                f"{datetime.datetime.now().strftime('%d_%H-%M-%S')}_{msg}.png",
            ),
            img,
        )
        super().__init__(args)


class CharacterIsStuckException(Exception): ...

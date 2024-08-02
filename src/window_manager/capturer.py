from logging import Logger
from threading import Event, RLock

import numpy

from src.exceptions import StoppedException
from src.window_manager.organizer import Organizer, WindowInfo
from src.window_manager.win32 import capture


class Capturer:
    def __init__(
        self,
        action_lock: RLock,
        organizer: Organizer,
        is_paused_event: Event,
        window_info: WindowInfo,
        logger: Logger,
    ) -> None:
        self.action_lock = action_lock
        self.organizer = organizer
        self.is_paused_event = is_paused_event
        self.window_info = window_info
        self.logger = logger

    def capture(self) -> numpy.ndarray:
        if self.is_paused_event.is_set():
            raise StoppedException()
        with self.action_lock:
            self.organizer.adjust_window_size()
            return capture(self.window_info.hwnd, self.logger)

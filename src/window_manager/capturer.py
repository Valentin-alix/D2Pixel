import numpy

from src.exceptions import StoppedException
from src.window_manager.organizer import Organizer
from src.window_manager.win32 import capture


class Capturer(Organizer):
    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

    def capture(self) -> numpy.ndarray:
        if self.is_paused:
            raise StoppedException()
        with self.action_lock:
            self.adjust_window_size()
            return capture(self.window_info.hwnd)

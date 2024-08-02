from ctypes import windll
from logging import Logger
from threading import Event, Lock, RLock

import numpy
import win32gui
import win32ui

from src.exceptions import NotPrintableWindow, StoppedException
from src.window_manager.organizer import Organizer
from src.window_manager.window_info import WindowInfo


class Capturer:
    def __init__(
        self,
        action_lock: RLock,
        organizer: Organizer,
        is_paused_event: Event,
        window_info: WindowInfo,
        logger: Logger,
        dc_lock: Lock,
    ) -> None:
        self.action_lock = action_lock
        self.organizer = organizer
        self.is_paused_event = is_paused_event
        self.window_info = window_info
        self.logger = logger
        self.dc_lock = dc_lock

    def capture(self) -> numpy.ndarray:
        def _get_window_dimensions() -> tuple[int, int]:
            windll.user32.SetProcessDPIAware()
            left, top, right, bot = win32gui.GetClientRect(self.window_info.hwnd)
            width = right - left
            height = bot - top
            return width, height

        def _get_compatible_bitmap(width: int, height: int):
            hwnd_dc = win32gui.GetWindowDC(self.window_info.hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            save_bit_map = win32ui.CreateBitmap()
            save_bit_map.CreateCompatibleBitmap(mfc_dc, width, height)

            save_dc.SelectObject(save_bit_map)

            return save_dc, save_bit_map, mfc_dc, hwnd_dc

        if self.is_paused_event.is_set():
            raise StoppedException()
        with self.action_lock:
            self.organizer.adjust_window_size()

            width, height = _get_window_dimensions()

            with self.dc_lock:
                save_dc, save_bit_map, mfc_dc, hwnd_dc = _get_compatible_bitmap(
                    width, height
                )
                result = windll.user32.PrintWindow(
                    self.window_info.hwnd, save_dc.GetSafeHdc(), 3
                )
                if result == 1:
                    bmp_info = save_bit_map.GetInfo()
                    bmp_str = save_bit_map.GetBitmapBits(True)

                    img = numpy.frombuffer(bmp_str, dtype="uint8")  # type: ignore
                    img.shape = (bmp_info["bmHeight"], bmp_info["bmWidth"], 4)
                    img = img[..., :3]
                    img = numpy.ascontiguousarray(img)

                win32gui.DeleteObject(save_bit_map.GetHandle())
                save_dc.DeleteDC()
                mfc_dc.DeleteDC()
                win32gui.ReleaseDC(self.window_info.hwnd, hwnd_dc)

            if result != 1:
                raise NotPrintableWindow()

            return img

import ctypes
from ctypes.wintypes import DWORD, HWND, RECT
from dataclasses import dataclass
from logging import Logger
from threading import Event
from time import sleep

import win32con
import win32gui

from src.exceptions import StoppedException
from src.window_manager.window_info import WindowInfo
from src.window_manager.window_searcher import get_process_name_by_window

dwmapi = ctypes.WinDLL("dwmapi")


OFFSET_BY_PROCESS_NAME: dict[str, tuple[int, int]] = {}


@dataclass
class Organizer:
    window_info: WindowInfo
    is_paused_event: Event
    target_window_width_height: tuple[int, int] | None
    logger: Logger

    def adjust_window_size(self):
        if self.is_paused_event.is_set():
            raise StoppedException()
        if self.target_window_width_height is not None:
            target_width, target_height = self.target_window_width_height
            window_place = win32gui.GetWindowPlacement(self.window_info.hwnd)[1]
            if window_place == win32con.SW_SHOWMINIMIZED:
                win32gui.ShowWindow(self.window_info.hwnd, win32con.SW_RESTORE)
                sleep(0.3)
                window_place = win32gui.GetWindowPlacement(self.window_info.hwnd)[1]

            if window_place == win32con.SW_SHOWMAXIMIZED:
                win32gui.ShowWindow(self.window_info.hwnd, win32con.SW_RESTORE)
                sleep(0.3)

            _, _, client_width, client_height = win32gui.GetClientRect(
                self.window_info.hwnd
            )

            start_x, start_y, end_x, end_y = win32gui.GetWindowRect(
                self.window_info.hwnd
            )

            process_name = get_process_name_by_window(self.window_info.hwnd)
            offset = OFFSET_BY_PROCESS_NAME.get(process_name)

            if (
                client_height == target_height
                and client_width == target_width
                and offset is not None
                and offset[0] == start_x
                and offset[1] == start_y
            ):
                return

            self.logger.info(
                f"Ajuste la taille de la fenetre pour {self.target_window_width_height}."
            )

            window_width = end_x - start_x
            window_height = end_y - start_y

            border_width = window_width - client_width
            title_bar_height = window_height - client_height

            new_window_height = target_height + title_bar_height
            new_window_width = target_width + border_width

            # get offsets from shadows
            rect = RECT()
            DMWA_EXTENDED_FRAME_BOUNDS = 9
            dwmapi.DwmGetWindowAttribute(
                HWND(self.window_info.hwnd),
                DWORD(DMWA_EXTENDED_FRAME_BOUNDS),
                ctypes.byref(rect),
                ctypes.sizeof(rect),
            )

            shadows: tuple[int, int, int, int] = (
                rect.left - start_x,
                rect.top - start_y,
                rect.right - end_x,
                rect.bottom - end_y,
            )
            offset_x: int = (shadows[2] - shadows[0]) // 2
            offset_y: int = -title_bar_height

            OFFSET_BY_PROCESS_NAME[process_name] = (offset_x, offset_y)

            win32gui.MoveWindow(
                self.window_info.hwnd,
                offset_x,
                offset_y,
                new_window_width,
                new_window_height,
                False,
            )

            sleep(0.3)
            win32gui.UpdateWindow(self.window_info.hwnd)
            win32gui.RedrawWindow(
                self.window_info.hwnd,
                None,  # type: ignore
                None,  # type: ignore
                win32con.RDW_INTERNALPAINT,
            )


def relink_windows_hwnd(
    previous_window_info: WindowInfo, new_windows_info: list[WindowInfo]
) -> bool:
    related_window = next(
        (
            window
            for window in new_windows_info
            if window.name == previous_window_info.name
        ),
        None,
    )
    if related_window is None:
        return False
    previous_window_info.hwnd = related_window.hwnd
    return True

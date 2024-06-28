import ctypes
from logging import Logger
import threading
from ctypes import windll
from ctypes.wintypes import DWORD, HWND, RECT
from time import sleep

import numpy
import win32con
import win32gui
import win32ui
from pynput.keyboard import Controller as KeyBoardController
from pynput.keyboard import Key as PyKey

from src.exceptions import NotPrintableWindow

dwmapi = ctypes.WinDLL("dwmapi")


def kill_window(hwnd: int):
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)


def get_foreground_window() -> int:
    return win32gui.GetForegroundWindow()


def set_foreground_window(hwnd: int):
    KeyBoardController().press(PyKey.alt)
    win32gui.SetForegroundWindow(hwnd)
    KeyBoardController().release(PyKey.alt)
    sleep(0.5)


def get_window_text(hwnd: int) -> str:
    return win32gui.GetWindowText(hwnd)


def set_maximized(hwnd: int):
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)


def is_window_visible(hwnd: int):
    return win32gui.IsWindowVisible(hwnd)


def set_restore(hwnd: int):
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)


class Rect:
    def __init__(self, left: int = 0, top: int = 0, right: int = 0, bottom: int = 0):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def __str__(self) -> str:
        return str((self.left, self.right, self.top, self.bottom))


def get_size_with_shadows(hwnd: int) -> tuple[int, int, Rect, Rect]:
    def get_window_rect(hwnd: int):
        rect = win32gui.GetWindowRect(hwnd)
        return Rect(rect[0], rect[1], rect[2], rect[3])

    def get_client_rect(hwnd: int):
        rect = win32gui.GetClientRect(hwnd)
        return Rect(rect[0], rect[1], rect[2], rect[3])

    exclude_shadow = get_client_rect(hwnd)
    include_shadow = get_window_rect(hwnd)

    shadow = Rect()
    shadow.left = include_shadow.left - exclude_shadow.left
    shadow.right = include_shadow.right - exclude_shadow.right
    shadow.top = include_shadow.top - exclude_shadow.top
    shadow.bottom = include_shadow.bottom - exclude_shadow.bottom

    width = (include_shadow.right + shadow.right) - (include_shadow.left + shadow.left)
    height = (include_shadow.bottom + shadow.bottom) - (include_shadow.top - shadow.top)

    return width, height, include_shadow, shadow


dc_lock = threading.Lock()  # used to avoid conflict between dc


def capture(hwnd: int, logger: Logger) -> numpy.ndarray:
    def get_window_dimensions(hwnd: int) -> tuple[int, int]:
        windll.user32.SetProcessDPIAware()
        left, top, right, bot = win32gui.GetClientRect(hwnd)
        width = right - left
        height = bot - top
        return width, height

    def get_compatible_bitmap(hwnd: int, width: int, height: int):
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        save_bit_map = win32ui.CreateBitmap()
        save_bit_map.CreateCompatibleBitmap(mfc_dc, width, height)

        save_dc.SelectObject(save_bit_map)

        return save_dc, save_bit_map, mfc_dc, hwnd_dc

    window_place = win32gui.GetWindowPlacement(hwnd)[1]
    if window_place == win32con.SW_SHOWMINIMIZED:
        logger.info("Restore la fenêtre.")
        set_restore(hwnd)
        sleep(1)

    width, height = get_window_dimensions(hwnd)

    with dc_lock:
        save_dc, save_bit_map, mfc_dc, hwnd_dc = get_compatible_bitmap(
            hwnd, width, height
        )
        result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)
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
        win32gui.ReleaseDC(hwnd, hwnd_dc)

    if result != 1:
        raise NotPrintableWindow()

    return img


def get_cursor_icon() -> numpy.ndarray:
    icon_width, icon_height = 32, 32

    cursor_info = win32gui.GetCursorInfo()
    cursor_handle = cursor_info[1]

    with dc_lock:
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, icon_width, icon_height)
        hdc = hdc.CreateCompatibleDC()
        hdc.SelectObject(hbmp)

        hdc.DrawIcon((0, 0), cursor_handle)

        bmp_str = hbmp.GetBitmapBits(True)

        img = numpy.frombuffer(bmp_str, dtype="uint8")  # type: ignore
        img.shape = (icon_width, icon_height, 4)
        img = img[..., :3]
        img = numpy.ascontiguousarray(img)

        win32gui.DeleteObject(hbmp.GetHandle())
        hdc.DeleteDC()

    return img


def adjust_window_size(
    hwnd: int, target_width: int, target_height: int, logger: Logger
):
    _, _, client_width, client_height = win32gui.GetClientRect(hwnd)

    if client_height == target_height and client_width == target_width:
        return

    logger.info(f"Ajuste la taille de la fenetre pour {target_width, target_height}.")

    start_x, start_y, end_x, end_y = win32gui.GetWindowRect(hwnd)

    window_width = end_x - start_x
    window_height = end_y - start_y

    border_width = window_width - client_width
    title_bar_height = window_height - client_height

    new_window_height = target_height + title_bar_height
    new_window_width = target_width + border_width

    window_place = win32gui.GetWindowPlacement(hwnd)[1]
    if window_place == win32con.SW_SHOWMINIMIZED:
        set_restore(hwnd)

    # get offsets from shadows
    rect = RECT()
    DMWA_EXTENDED_FRAME_BOUNDS = 9
    dwmapi.DwmGetWindowAttribute(
        HWND(hwnd),
        DWORD(DMWA_EXTENDED_FRAME_BOUNDS),
        ctypes.byref(rect),
        ctypes.sizeof(rect),
    )

    shadows = (
        rect.left - start_x,
        rect.top - start_y,
        rect.right - end_x,
        rect.bottom - end_y,
    )
    offset_x = (shadows[2] - shadows[0]) // 2
    offset_y = (shadows[3] - shadows[1]) // 2

    win32gui.MoveWindow(
        hwnd,
        offset_x,
        offset_y,
        new_window_width,
        new_window_height,
        False,
    )

    sleep(1)
    win32gui.UpdateWindow(hwnd)

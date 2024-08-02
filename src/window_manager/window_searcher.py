from logging import Logger

import psutil
import win32gui
import win32process
from win32process import GetWindowThreadProcessId

from src.window_manager.window_info import WindowInfo


def get_windows() -> list[WindowInfo]:
    windows: list[WindowInfo] = []

    def win_enum_handler(hwnd: int, _: None):
        window_text = win32gui.GetWindowText(hwnd)
        windows.append(WindowInfo(hwnd=hwnd, name=window_text))

    win32gui.EnumWindows(win_enum_handler, None)

    return windows


def get_windows_by_process_and_name(
    target_process_name: str | None = None,
    target_name: str | None = None,
    check_visible: bool = True,
) -> list[WindowInfo]:
    windows_target: list[WindowInfo] = []

    for window in get_windows():
        if check_visible and not win32gui.IsWindowVisible(window.hwnd):
            continue
        if target_process_name is not None:
            pid = win32process.GetWindowThreadProcessId(window.hwnd)
            try:
                process_name = psutil.Process(pid[1]).name()
            except psutil.NoSuchProcess:
                continue
            if not process_name == target_process_name:
                continue
        window_text = win32gui.GetWindowText(window.hwnd)
        if target_name and not window_text == target_name:
            continue
        windows_target.append(WindowInfo(hwnd=window.hwnd, name=window_text))

    return windows_target


def get_dofus_window_infos() -> list[WindowInfo]:
    return get_windows_by_process_and_name(target_process_name="Dofus.exe")


def get_ankama_window_info(logger: Logger) -> WindowInfo | None:
    windows_ankama = get_windows_by_process_and_name("Ankama Launcher.exe")
    logger.info(f"Found ankama windows : {windows_ankama}")
    if len(windows_ankama) == 0:
        return None
    return windows_ankama[0]


def get_process_name_by_window(hwnd: int) -> str:
    _, process_id = GetWindowThreadProcessId(hwnd)
    process = psutil.Process(process_id)
    process_name = process.name()
    return process_name

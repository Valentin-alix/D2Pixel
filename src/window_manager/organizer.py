from logging import Logger
from threading import Event
import psutil
import win32gui
import win32process
from pydantic import BaseModel, ConfigDict

from src.exceptions import StoppedException
from src.window_manager.win32 import adjust_window_size


class WindowInfo(BaseModel):
    hwnd: int
    name: str

    def __hash__(self) -> int:
        return self.hwnd.__hash__()


class Organizer(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    window_info: WindowInfo
    is_paused: Event
    target_window_size: tuple[int, int]
    logger: Logger

    def adjust_window_size(self):
        if self.is_paused.is_set():
            raise StoppedException()
        if self.target_window_size is not None:
            adjust_window_size(
                self.window_info.hwnd, *self.target_window_size, self.logger
            )


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
    windows_ankama = get_windows_by_process_and_name(
        "Ankama Launcher.exe", "Ankama Launcher", False
    )
    logger.info(f"Found ankama windows : {windows_ankama}")
    if len(windows_ankama) == 0:
        return None
    return windows_ankama[0]

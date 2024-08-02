from src.window_manager.window_info import (
    WindowInfo,
)
from src.window_manager.window_searcher import get_windows_by_process_and_name


def get_first_window_dofus() -> WindowInfo | None:
    for window in get_windows_by_process_and_name(target_process_name="Dofus.exe"):
        return window

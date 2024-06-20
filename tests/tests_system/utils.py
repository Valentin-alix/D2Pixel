from threading import RLock

from src.window_manager.organizer import (
    WindowInfo,
    get_windows_by_process_and_name,
)


def get_first_window_dofus() -> WindowInfo | None:
    for window in get_windows_by_process_and_name(target_process_name="Dofus.exe"):
        return window


def get_base_params_system():
    return {"window": get_first_window_dofus(), "lock": RLock()}

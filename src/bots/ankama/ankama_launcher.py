import subprocess
from threading import Thread
from time import sleep

import schedule
from dotenv import get_key, set_key
from EzreD2Shared.shared.consts.adaptative.positions import EMPTY_POSITION
from EzreD2Shared.shared.consts.object_configs import ObjectConfigs

from src.bots.ankama.ankama_bot import AnkamaBot
from src.bots.dofus.connection.connection_system import (
    ConnectionSystem,
)
from src.bots.modules.module_manager import ModuleManager
from src.common.retry import RetryTimeArgs
from src.common.scheduler import run_continuously
from src.common.searcher import search_for_file
from src.consts import ENV_PATH
from src.gui.signals.dofus_signals import DofusSignals
from src.window_manager.organizer import (
    WindowInfo,
    get_ankama_window_info,
    get_dofus_window_infos,
    get_windows_by_process_and_name,
)
from src.window_manager.win32 import is_window_visible

RANGES_HOURS_PLAYTIME: list[tuple[str, str]] = [
    ("08:00", "12:30"),
    ("13:00", "20:30"),
    ("21:00", "23:45"),
]


def get_path_ankama_launcher() -> str:
    path = get_key(ENV_PATH, "PATH_ANKAMA_LAUNCHER")
    if path is not None:
        return path
    path = search_for_file("Ankama Launcher.exe")
    set_key(ENV_PATH, "PATH_ANKAMA_LAUNCHER", path)
    return path


def launch_launcher():
    subprocess.Popen(
        [get_path_ankama_launcher()],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    sleep(3)


class AnkamaLauncher(AnkamaBot):
    def __init__(self) -> None:
        if not (window_info := get_ankama_window_info()):
            # launcher not found, launch...
            launch_launcher()
            sleep(2)
            window_info = get_ankama_window_info()
            assert window_info is not None

        self.pause_threads: list[Thread] | None = None
        super().__init__(window_info=window_info)

    def launch_games(self):
        """launch games by clicking play on ankama launcher & wait 12 seconds"""
        if not is_window_visible(self.window_info.hwnd):
            launch_launcher()  # to have window visible

        self.click(EMPTY_POSITION)  # to defocus play button
        pos, _, config, _ = self.wait_multiple_or_template(
            [ObjectConfigs.Ankama.play, ObjectConfigs.Ankama.empty_play],
            force=True,
            retry_time_args=RetryTimeArgs(timeout=15, offset_start=1),
        )
        if config == ObjectConfigs.Ankama.play:
            self.click(pos)
            sleep(12)

    def connect_all(self) -> list[WindowInfo]:
        self.launch_games()
        windows_dofus = self.connect_windows(get_dofus_window_infos())
        return windows_dofus

    def connect_window(self, window_info: WindowInfo, wait_play: bool = False):
        connecter = ConnectionSystem(
            window_info=window_info, bot_signals=DofusSignals()
        )
        if wait_play:
            connecter.wait_on_screen(
                ObjectConfigs.Connection.play,
                force=True,
                retry_time_args=RetryTimeArgs(offset_start=3, timeout=30),
            )
        while not connecter.connect_character(connecter.capture())[1]:
            sleep(1)
        connecter.clean_interface(connecter.capture())
        self.log_info(f"{connecter.character} is connected")
        connecter.is_connected.set()

    def connect_windows(
        self, dofus_windows_info: list[WindowInfo], wait_play: bool = False
    ) -> list[WindowInfo]:
        """connect all window & retrieve new window name after connected

        Args:
            wait_play (bool, optional): if set to True then wait for play from character selection. Defaults to False.

        Returns:
            list[WindowInfo]: the refreshed new windows dofus
        """
        for window_info in dofus_windows_info:
            self.connect_window(window_info, wait_play)

        return get_windows_by_process_and_name(target_process_name="Dofus.exe")

    def run_playtime_planner(self, modules_managers: list[ModuleManager]):
        def pause_bots(modules_managers: list[ModuleManager]):
            def pause_bot(module_manager: ModuleManager):
                if not module_manager.is_playing:
                    return
                while module_manager.in_fight:
                    sleep(0.5)
                module_manager.internal_pause = True
                with module_manager.action_lock:
                    module_manager.log_info("Paused bot")
                    module_manager.is_connected.clear()
                    module_manager.kill_window()
                    while True:
                        if not module_manager.internal_pause:
                            break
                        if module_manager.is_paused:
                            break
                        sleep(0.5)

            self.pause_threads = []
            for module_manager in modules_managers:
                pause_thread = Thread(
                    target=lambda: pause_bot(module_manager), daemon=True
                )
                pause_thread.start()
                self.pause_threads.append(pause_thread)

        def resume_bots(modules_managers: list[ModuleManager]):
            if not any(elem.is_playing for elem in modules_managers):
                return
            dofus_windows_info = self.connect_all()
            for module_manager in modules_managers:
                if module_manager.is_playing:
                    module_manager.log_info("Resume bot")
                related_window = next(
                    window
                    for window in dofus_windows_info
                    if window.name == module_manager.window_info.name
                )
                module_manager.window_info.hwnd = related_window.hwnd
                module_manager.internal_pause = False

        for start_hour, end_hour in RANGES_HOURS_PLAYTIME:
            schedule.every().day.at(end_hour).do(lambda: pause_bots(modules_managers))
            schedule.every().day.at(start_hour).do(
                lambda: resume_bots(modules_managers)
            )

        run_continuously()

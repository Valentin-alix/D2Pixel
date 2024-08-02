import os
import subprocess
from logging import Logger
from threading import Event, Lock, RLock, Thread
from time import sleep

import win32gui
from dotenv import get_key, set_key

from D2Shared.shared.consts.adaptative.positions import EMPTY_POSITION
from D2Shared.shared.consts.object_configs import ObjectConfigs
from src.consts import ANKAMA_WINDOW_SIZE, ENV_PATH
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from src.utils.retry import RetryTimeArgs
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller
from src.window_manager.organizer import (
    Organizer,
)
from src.window_manager.window_info import WindowInfo
from src.window_manager.window_searcher import get_ankama_window_info


def get_path_ankama_launcher() -> str:
    path = get_key(ENV_PATH, "PATH_ANKAMA_LAUNCHER")
    if path is not None:
        return path
    ankama_exe_filename = "Ankama Launcher.exe"
    for root, _, files in os.walk("C:\\"):
        if ankama_exe_filename in files:
            path = os.path.join(root, ankama_exe_filename)
            break
    else:
        raise FileNotFoundError(f"Did not found {ankama_exe_filename}")

    set_key(ENV_PATH, "PATH_ANKAMA_LAUNCHER", path)
    return path


def launch_launcher():
    subprocess.Popen(
        [get_path_ankama_launcher()],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def get_or_launch_ankama_window(logger: Logger) -> WindowInfo:
    if not (window_info := get_ankama_window_info(logger)):
        logger.info("Launch launcher")
        launch_launcher()
        while True:
            window_info = get_ankama_window_info(logger)
            if window_info is not None:
                break
            logger.info(
                "N'a pas trouvé de fenêtre correspondant à l'Ankama Launcher..."
            )
            sleep(0.5)
    return window_info


class AnkamaLauncher:
    def __init__(
        self,
        window_info: WindowInfo,
        logger: Logger,
        service: ServiceSession,
        dc_lock: Lock,
    ) -> None:
        self.pause_threads: list[Thread] | None = None

        self.service = service
        self.action_lock = RLock()
        self.dc_lock = dc_lock
        self.logger = logger
        self.is_paused_event = Event()
        self.window_info: WindowInfo = window_info
        self.organizer = Organizer(
            window_info=window_info,
            is_paused_event=self.is_paused_event,
            target_window_width_height=ANKAMA_WINDOW_SIZE,
            logger=self.logger,
        )
        self.controller = Controller(
            logger=self.logger,
            window_info=window_info,
            is_paused_event=self.is_paused_event,
            organizer=self.organizer,
            action_lock=self.action_lock,
        )
        capturer = Capturer(
            action_lock=self.action_lock,
            organizer=self.organizer,
            is_paused_event=self.is_paused_event,
            window_info=window_info,
            logger=self.logger,
            dc_lock=dc_lock,
        )
        object_searcher = ObjectSearcher(self.logger, self.service)
        self.image_manager = ImageManager(capturer, object_searcher, self.dc_lock)

    def launch_dofus_games(self):
        ank_window_info = get_or_launch_ankama_window(self.logger)
        self.window_info.hwnd = ank_window_info.hwnd

        """launch games by clicking play on ankama launcher & wait 12 seconds"""
        if not win32gui.IsWindowVisible(self.window_info.hwnd):
            self.logger.info("Launch launcher for visible window")
            launch_launcher()  # to have window visible
        else:
            self.controller.click(EMPTY_POSITION)  # to defocus play button
        pos, _, config, _ = self.image_manager.wait_multiple_or_template(
            [ObjectConfigs.Ankama.play, ObjectConfigs.Ankama.empty_play],
            force=True,
            retry_time_args=RetryTimeArgs(timeout=35, offset_start=1),
        )
        if config == ObjectConfigs.Ankama.play:
            self.controller.click(pos)
            sleep(15)

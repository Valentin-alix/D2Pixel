import subprocess
from logging import Logger
from threading import Event, RLock, Thread
from time import sleep

from dotenv import get_key, set_key

from D2Shared.shared.consts.adaptative.positions import EMPTY_POSITION
from D2Shared.shared.consts.object_configs import ObjectConfigs
from src.common.retry import RetryTimeArgs
from src.common.searcher import search_for_file
from src.consts import ANKAMA_WINDOW_SIZE, ENV_PATH
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller
from src.window_manager.organizer import (
    Organizer,
    WindowInfo,
    get_ankama_window_info,
)
from src.window_manager.win32 import is_window_visible


class AnkamaLauncher:
    def __init__(self, logger: Logger, service: ServiceSession) -> None:
        self.pause_threads: list[Thread] | None = None

        self.service = service
        self.action_lock = RLock()
        self.logger = logger
        self.is_paused_event = Event()
        self.window_info: WindowInfo | None = None
        self._is_init_launcher: bool = False

    def _init_launcher_by_window(self, window_info: WindowInfo):
        if self._is_init_launcher:
            self.logger.info("Le launcher est déjà initialisé.")
            return
        self.organizer = Organizer(
            window_info=window_info,
            is_paused_event=self.is_paused_event,
            target_window_size=ANKAMA_WINDOW_SIZE,
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
        )
        object_searcher = ObjectSearcher(self.logger, self.service)
        self.image_manager = ImageManager(capturer, object_searcher)

    def launch_dofus_games(self):
        ank_window_info = self.get_or_launch_ankama_window()
        if self.window_info is None:
            self.window_info = ank_window_info
        else:
            self.window_info.hwnd = ank_window_info.hwnd
        self._init_launcher_by_window(self.window_info)

        """launch games by clicking play on ankama launcher & wait 12 seconds"""
        if not is_window_visible(self.window_info.hwnd):
            self.logger.info("Launch launcher for visible window")
            self._launch_launcher()  # to have window visible
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

    def get_or_launch_ankama_window(self) -> WindowInfo:
        if not (window_info := get_ankama_window_info(self.logger)):
            self.logger.info("Launch launcher")
            self._launch_launcher()
            while True:
                window_info = get_ankama_window_info(self.logger)
                if window_info is not None:
                    break
                self.logger.info(
                    "N'a pas trouvé de fenêtre correspondant à l'Ankama Launcher..."
                )
                sleep(0.5)
        return window_info

    def _launch_launcher(self):
        subprocess.Popen(
            [self._get_path_ankama_launcher()],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    def _get_path_ankama_launcher(self) -> str:
        path = get_key(ENV_PATH, "PATH_ANKAMA_LAUNCHER")
        if path is not None:
            return path
        path = search_for_file("Ankama Launcher.exe")
        set_key(ENV_PATH, "PATH_ANKAMA_LAUNCHER", path)
        return path

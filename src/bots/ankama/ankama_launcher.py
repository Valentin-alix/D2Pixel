from logging import Logger
import subprocess
from threading import Event, RLock, Thread
from time import sleep

import schedule
from dotenv import get_key, set_key
from D2Shared.shared.consts.adaptative.positions import EMPTY_POSITION
from D2Shared.shared.consts.object_configs import ObjectConfigs

from D2Shared.shared.schemas.user import ReadUserSchema
from src.bots.dofus.connection.connection_system import (
    ConnectionSystem,
)
from src.bots.dofus.fight.fight_system import FightSystem
from src.bots.dofus.fight.grid.grid import Grid
from src.bots.dofus.fight.grid.ldv_grid import LdvGrid
from src.bots.dofus.fight.grid.path_grid import AstarGrid
from src.bots.dofus.fight.ias.base import IaBaseFightSystem
from src.bots.dofus.fight.ias.brute import IaBruteFightSystem
from src.bots.dofus.fight.spells.spell_manager import SpellManager
from src.bots.dofus.fight.spells.spell_system import SpellSystem
from src.bots.dofus.hud.hud_system import Hud, HudSystem
from src.bots.dofus.hud.info_popup.job_level import JobParser
from src.bots.dofus.walker.core_walker_system import CoreWalkerSystem
from src.bots.modules.module_manager import ModuleManager
from src.common.retry import RetryTimeArgs
from src.common.scheduler import run_continuously
from src.common.searcher import search_for_file
from src.consts import ANKAMA_WINDOW_SIZE, DOFUS_WINDOW_SIZE, ENV_PATH
from src.image_manager.animation import AnimationManager
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from src.states.character_state import CharacterState
from src.states.map_state import MapState
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller
from src.window_manager.organizer import (
    Organizer,
    WindowInfo,
    get_ankama_window_info,
    get_dofus_window_infos,
    get_windows_by_process_and_name,
)
from src.window_manager.win32 import is_window_visible


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


class AnkamaLauncher:
    def __init__(
        self, logger: Logger, service: ServiceSession, user: ReadUserSchema
    ) -> None:
        if not (window_info := get_ankama_window_info(logger)):
            # launcher not found, launch...
            launch_launcher()
            while True:
                window_info = get_ankama_window_info(logger)
                if window_info is not None:
                    break
                sleep(1)

        self.pause_threads: list[Thread] | None = None

        self.service = service
        self.window_info = window_info
        self.action_lock = RLock()
        self.logger = logger
        self.is_paused = Event()
        self.organizer = Organizer(
            window_info=window_info,
            is_paused=self.is_paused,
            target_window_size=ANKAMA_WINDOW_SIZE,
            logger=self.logger,
        )
        self.controller = Controller(
            logger=self.logger,
            window_info=window_info,
            is_paused=self.is_paused,
            organizer=self.organizer,
            action_lock=self.action_lock,
        )
        capturer = Capturer(
            action_lock=self.action_lock,
            organizer=self.organizer,
            is_paused=self.is_paused,
            window_info=window_info,
            logger=self.logger,
        )
        self.user = user
        object_searcher = ObjectSearcher(self.service)
        self.image_manager = ImageManager(capturer, object_searcher)

    def launch_games(self):
        """launch games by clicking play on ankama launcher & wait 12 seconds"""
        if not is_window_visible(self.window_info.hwnd):
            launch_launcher()  # to have window visible

        self.controller.click(EMPTY_POSITION)  # to defocus play button
        pos, _, config, _ = self.image_manager.wait_multiple_or_template(
            [ObjectConfigs.Ankama.play, ObjectConfigs.Ankama.empty_play],
            force=True,
            retry_time_args=RetryTimeArgs(timeout=15, offset_start=1),
        )
        if config == ObjectConfigs.Ankama.play:
            self.controller.click(pos)
            sleep(12)

    def connect_all(self) -> list[WindowInfo]:
        self.launch_games()
        windows_dofus = self.connect_windows(get_dofus_window_infos())
        return windows_dofus

    def connect_window(self, window_info: WindowInfo, wait_play: bool = False):
        organizer = Organizer(
            window_info=window_info,
            is_paused=self.is_paused,
            target_window_size=DOFUS_WINDOW_SIZE,
            logger=self.logger,
        )
        action_lock = RLock()
        capturer = Capturer(
            action_lock=action_lock,
            organizer=organizer,
            is_paused=self.is_paused,
            window_info=window_info,
            logger=self.logger,
        )
        animation_manager = AnimationManager(capturer=capturer)
        object_searcher = ObjectSearcher(self.service)
        image_manager = ImageManager(capturer, object_searcher)
        grid = Grid(object_searcher)
        character_id = window_info.name.split(" - Dofus")[0]
        character_state = CharacterState(self.service, character_id)
        spell_manager = SpellManager(grid, self.service, character_state)

        controller = Controller(
            self.logger, window_info, self.is_paused, organizer, action_lock
        )
        spell_sys = SpellSystem(
            self.service,
            spell_manager,
            controller,
            capturer,
            object_searcher,
            image_manager,
            animation_manager,
            grid,
            self.logger,
        )
        astar_grid = AstarGrid(grid, self.logger)
        ldv_grid = LdvGrid(grid)
        ia_base_sys = IaBaseFightSystem(
            spell_sys,
            grid,
            ldv_grid,
            controller,
            animation_manager,
            self.service,
            character_state,
            self.logger,
            spell_manager,
            object_searcher,
        )
        ia_brute_sys = IaBruteFightSystem(
            ia_base_sys,
            spell_sys,
            spell_manager,
            astar_grid,
            grid,
            self.logger,
            self.service,
            character_state,
        )
        hud = Hud(logger=self.logger)
        job_parser = JobParser(service=self.service, logger=self.logger)
        hud_sys = HudSystem(
            hud=hud,
            image_manager=image_manager,
            character_state=character_state,
            service=self.service,
            controller=controller,
            object_searcher=object_searcher,
            capturer=capturer,
            logger=self.logger,
            job_parser=job_parser,
        )
        map_state = MapState()
        core_walker_sys = CoreWalkerSystem(
            hud_sys,
            self.logger,
            map_state,
            character_state,
            controller,
            image_manager,
            object_searcher,
            animation_manager,
            capturer,
            self.service,
            self.user,
        )
        fight_sys = FightSystem(
            ia_brute_sys,
            core_walker_sys,
            animation_manager,
            hud_sys,
            astar_grid,
            spell_manager,
            self.logger,
            capturer,
            object_searcher,
            image_manager,
            controller,
            grid,
            Event(),
            self.service,
            Event(),
        )
        connecter = ConnectionSystem(
            fight_sys,
            hud_sys,
            controller,
            object_searcher,
            capturer,
            image_manager,
            self.logger,
            Event(),
            Event(),
        )
        if wait_play:
            image_manager.wait_on_screen(
                ObjectConfigs.Connection.play,
                force=True,
                retry_time_args=RetryTimeArgs(offset_start=3, timeout=30),
            )
        while not connecter.connect_character(capturer.capture())[1]:
            sleep(1)
        hud_sys.clean_interface(capturer.capture())
        self.logger.info(f"{character_state.character} est connecté.")
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
                if not module_manager.is_playing.is_set():
                    return
                module_manager.fighter.fight_sys.not_in_fight.wait()
                module_manager.internal_pause.set()
                with module_manager.action_lock:
                    module_manager.logger.info("Bot mis en pause.")
                    module_manager.is_connected.clear()
                    module_manager.controller.kill_window()
                    while True:
                        if not module_manager.internal_pause.is_set():
                            break
                        if module_manager.is_paused.is_set():
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
            if not any(elem.is_playing.is_set() for elem in modules_managers):
                return
            dofus_windows_info = self.connect_all()
            for module_manager in modules_managers:
                if module_manager.is_playing.is_set():
                    module_manager.logger.info("Bot sortit de pause.")
                related_window = next(
                    window
                    for window in dofus_windows_info
                    if window.name == module_manager.window_info.name
                )
                module_manager.window_info.hwnd = related_window.hwnd
                module_manager.internal_pause.clear()

        for range_hour_playtime in self.user.config_user.ranges_hour_playtime:
            schedule.every().day.at(range_hour_playtime.end_time.strftime("%H:%M")).do(
                lambda: pause_bots(modules_managers)
            )
            schedule.every().day.at(
                range_hour_playtime.start_time.strftime("%H:%M")
            ).do(lambda: resume_bots(modules_managers))

        run_continuously()

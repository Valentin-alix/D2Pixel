import subprocess
import traceback
from logging import Logger
from threading import Event, RLock, Thread
from time import sleep

import schedule
from dotenv import get_key, set_key

from D2Shared.shared.consts.adaptative.positions import EMPTY_POSITION
from D2Shared.shared.consts.object_configs import ObjectConfigs
from D2Shared.shared.schemas.user import ReadUserSchema
from src.bots.dofus.connection.connection_system import ConnectionSystem
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
from src.bots.modules.bot import Bot
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
)
from src.window_manager.win32 import is_window_visible


class AnkamaLauncher:
    def __init__(
        self, logger: Logger, service: ServiceSession, user: ReadUserSchema
    ) -> None:
        self.pause_threads: list[Thread] | None = None

        self.user = user
        self.service = service
        self.action_lock = RLock()
        self.logger = logger
        self.is_paused = Event()
        self.window_info: WindowInfo | None = None
        self.is_init_launcher: bool = False
        self.is_init_playtime_planner: bool = False

    def launch_dofus_game(self):
        ank_window_info = self.get_window_info()
        if self.window_info is None:
            self.window_info = ank_window_info
        else:
            self.window_info.hwnd = ank_window_info.hwnd
        self.init_launcher(self.window_info)

        """launch games by clicking play on ankama launcher & wait 12 seconds"""
        if not is_window_visible(self.window_info.hwnd):
            self.logger.info("Launch launcher for visible window")
            self._launch_launcher()  # to have window visible

        self.controller.click(EMPTY_POSITION)  # to defocus play button
        pos, _, config, _ = self.image_manager.wait_multiple_or_template(
            [ObjectConfigs.Ankama.play, ObjectConfigs.Ankama.empty_play],
            force=True,
            retry_time_args=RetryTimeArgs(timeout=35, offset_start=1),
        )
        if config == ObjectConfigs.Ankama.play:
            self.controller.click(pos)
            sleep(15)

    def connect_all_dofus_account(self) -> list[WindowInfo]:
        self.launch_dofus_game()
        dofus_windows_info = get_dofus_window_infos()
        for window_info in dofus_windows_info:
            while True:
                try:
                    self.connect_dofus_account(window_info)
                except Exception:
                    self.logger.error(traceback.format_exc())
                    continue
                break
        return get_dofus_window_infos()

    def connect_dofus_account(self, window_info: WindowInfo, wait_play: bool = False):
        character_id = window_info.name.split(" - Dofus")[0]

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
        animation_manager = AnimationManager(logger=self.logger, capturer=capturer)
        object_searcher = ObjectSearcher(self.logger, self.service)
        image_manager = ImageManager(capturer, object_searcher)
        grid = Grid(self.logger, object_searcher)

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
        )
        if wait_play:
            image_manager.wait_on_screen(
                ObjectConfigs.Connection.play,
                force=True,
                retry_time_args=RetryTimeArgs(offset_start=3, timeout=30),
            )
        while not connecter.connect_character(capturer.capture())[1]:
            sleep(0.3)
        self.logger.info(f"{character_state.character} est connecté.")
        connecter.is_connected.set()

    def relink_windows_dofus_hwnd(
        self, previous_window_info: WindowInfo, dofus_windows_info: list[WindowInfo]
    ) -> bool:
        related_window = next(
            (
                window
                for window in dofus_windows_info
                if window.name == previous_window_info.name
            ),
            None,
        )
        if related_window is None:
            return False
        previous_window_info.hwnd = related_window.hwnd
        return True

    def init_launcher(self, window_info: WindowInfo):
        if self.is_init_launcher:
            self.logger.info("Le launcher est déjà initialisé.")
            return
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
        object_searcher = ObjectSearcher(self.logger, self.service)
        self.image_manager = ImageManager(capturer, object_searcher)

    def get_window_info(self) -> WindowInfo:
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

    def run_playtime_planner(self, bots_by_id: dict[str, Bot]):
        if self.is_init_playtime_planner:
            return
        self.is_init_playtime_planner = True

        def pause_bots(bots_by_id: dict[str, Bot]):
            def pause_bot(bot: Bot):
                if bot.window_info is None:
                    bot.logger.info("Bot is not initialized, skipping pause.")
                    return
                while True:
                    if not bot.is_playing.is_set() or bot.is_paused.is_set():
                        return
                    if bot.fighter.fight_sys.not_in_fight.is_set():
                        break
                    bot.logger.info("En attente que le bot ne soit plus en combat...")
                    sleep(0.5)
                bot.internal_pause.set()
                with bot.action_lock:
                    bot.logger.info("Bot mis en pause.")
                    bot.is_connected.clear()
                    bot.controller.kill_window()
                    while True:
                        if not bot.internal_pause.is_set():
                            break
                        if bot.is_paused.is_set():
                            break
                        sleep(0.5)

            self.pause_threads = []
            for bot in bots_by_id.values():
                pause_thread = Thread(target=lambda: pause_bot(bot), daemon=True)
                pause_thread.start()
                self.pause_threads.append(pause_thread)

        def resume_bots(bots_by_id: dict[str, Bot]):
            if not any(
                elem.window_info and elem.is_playing.is_set()
                for elem in bots_by_id.values()
            ):
                self.logger.info("Aucun bot n'est initialisé ou en train de jouer.")
                return
            dofus_windows_info = self.connect_all_dofus_account()
            for bot in bots_by_id.values():
                if bot.window_info is None or not bot.is_playing.is_set():
                    continue
                bot.logger.info("Bot sortit de pause.")
                if not self.relink_windows_dofus_hwnd(
                    bot.window_info, dofus_windows_info
                ):
                    bot.logger.info("Did not found related new window, retrying...")
                    return resume_bots(bots_by_id)
                bot.internal_pause.clear()
                bot.is_connected.set()

        for range_hour_playtime in self.user.config_user.ranges_hour_playtime:
            schedule.every().day.at(range_hour_playtime.end_time.strftime("%H:%M")).do(
                lambda: pause_bots(bots_by_id)
            )
            schedule.every().day.at(
                range_hour_playtime.start_time.strftime("%H:%M")
            ).do(lambda: resume_bots(bots_by_id))

        run_continuously()

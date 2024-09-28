import traceback
from dataclasses import dataclass
from logging import Logger
from threading import Event, Lock, RLock, Thread
from time import sleep

from D2Shared.shared.consts.object_configs import ObjectConfigs
from D2Shared.shared.schemas.user import ReadUserSchema
from src.bots.dofus.connection.connection_system import ConnectionSystem
from src.bots.dofus.deblocker.blocked import Blocked
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
from src.consts import DOFUS_WINDOW_SIZE
from src.image_manager.animation import AnimationManager
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from src.states.character_state import CharacterState
from src.states.map_state import MapState
from src.utils.retry import RetryTimeArgs
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller
from src.window_manager.organizer import (
    Organizer,
)
from src.window_manager.window_info import WindowInfo
from src.window_manager.window_searcher import get_dofus_window_infos


@dataclass
class ConnectionManager:
    logger: Logger
    service: ServiceSession
    user: ReadUserSchema
    dc_lock: Lock

    def connect_all_dofus_account(self) -> list[WindowInfo]:
        dofus_windows_info = get_dofus_window_infos()
        threads_connect_dofus: list[Thread] = []
        for window_info in dofus_windows_info:
            threads_connect_dofus.append(
                Thread(
                    target=self.connect_dofus_account, args=(window_info,), daemon=True
                )
            )
        for thread in threads_connect_dofus:
            thread.start()

        for thread in threads_connect_dofus:
            thread.join()

        return get_dofus_window_infos()

    def connect_dofus_account(
        self, window_info: WindowInfo, wait_play: bool = False
    ) -> None:
        character_id = window_info.name.split(" - Dofus")[0]

        is_connected_event = Event()
        is_in_fight_event = Event()
        is_paused_event = Event()

        organizer = Organizer(
            window_info=window_info,
            is_paused_event=is_paused_event,
            target_window_width_height=DOFUS_WINDOW_SIZE,
            logger=self.logger,
        )
        action_lock = RLock()
        capturer = Capturer(
            action_lock=action_lock,
            organizer=organizer,
            is_paused_event=is_paused_event,
            window_info=window_info,
            logger=self.logger,
            dc_lock=self.dc_lock,
        )
        animation_manager = AnimationManager(logger=self.logger, capturer=capturer)
        object_searcher = ObjectSearcher(self.logger, self.service)
        image_manager = ImageManager(capturer, object_searcher, self.dc_lock)
        grid = Grid(self.logger, object_searcher)

        character_state = CharacterState(self.service, character_id)
        spell_manager = SpellManager(grid, self.service, character_state)

        controller = Controller(
            self.logger, window_info, is_paused_event, organizer, action_lock
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
        blocked = Blocked(capturer=capturer, object_searcher=object_searcher, hud=hud)
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
            blocked=blocked,
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
            self.service,
            is_in_fight_event,
        )
        connecter = ConnectionSystem(
            fight_system=fight_sys,
            hud_system=hud_sys,
            controller=controller,
            object_searcher=object_searcher,
            image_manager=image_manager,
            logger=self.logger,
            is_connected_event=is_connected_event,
        )
        while True:
            try:
                if wait_play:
                    image_manager.wait_on_screen(
                        ObjectConfigs.Connection.play,
                        force=True,
                        retry_time_args=RetryTimeArgs(offset_start=3, timeout=30),
                    )
                while not connecter.connect_character(capturer.capture())[1]:
                    sleep(1)
                self.logger.info(f"{character_state.character} est connecté.")
            except Exception:
                self.logger.error(traceback.format_exc())
                sleep(1)
                continue
            break

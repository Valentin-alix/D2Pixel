import unittest
from logging import Logger
from threading import Event, RLock

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
from src.consts import DOFUS_WINDOW_SIZE
from src.gui.signals.app_signals import AppSignals
from src.image_manager.animation import AnimationManager
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from src.services.user import UserService
from src.states.character_state import CharacterState
from src.states.map_state import MapState
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller
from src.window_manager.organizer import Organizer
from tests.tests_system.utils import get_first_window_dofus


@unittest.skipIf((window := get_first_window_dofus()) is None, "")
class TestConnectionSystem(unittest.TestCase):
    def setUp(self) -> None:
        assert window is not None

        logger = Logger("root")
        service = ServiceSession(logger=logger, app_signals=AppSignals())
        is_paused = Event()
        organizer = Organizer(
            window_info=window,
            is_paused_event=is_paused,
            target_window_size=DOFUS_WINDOW_SIZE,
            logger=logger,
        )
        action_lock = RLock()
        controller = Controller(
            logger=logger,
            window_info=window,
            is_paused_event=is_paused,
            organizer=organizer,
            action_lock=action_lock,
        )
        self.capturer = Capturer(
            action_lock=action_lock,
            organizer=organizer,
            is_paused_event=is_paused,
            window_info=window,
            logger=logger,
        )
        object_searcher = ObjectSearcher(logger=logger, service=service)
        image_manager = ImageManager(
            capturer=self.capturer, object_searcher=object_searcher
        )
        animation_manager = AnimationManager(capturer=self.capturer, logger=logger)
        grid = Grid(logger=logger, object_searcher=object_searcher)
        ldv_grid = LdvGrid(grid=grid)
        astar_grid = AstarGrid(grid=grid, logger=logger)
        char_state = CharacterState(service=service, character_id="temp")
        spell_manager = SpellManager(
            grid=grid, service=service, character_state=char_state
        )
        spell_sys = SpellSystem(
            service=service,
            spell_manager=spell_manager,
            controller=controller,
            capturer=self.capturer,
            object_searcher=object_searcher,
            image_manager=image_manager,
            animation_manager=animation_manager,
            grid=grid,
            logger=logger,
        )
        ia_base = IaBaseFightSystem(
            spell_sys=spell_sys,
            grid=grid,
            ldv_grid=ldv_grid,
            controller=controller,
            animation_manager=animation_manager,
            service=service,
            character_state=char_state,
            logger=logger,
            spell_manager=spell_manager,
            object_searcher=object_searcher,
        )
        ia_brute = IaBruteFightSystem(
            ia_base_fight_sys=ia_base,
            spell_system=spell_sys,
            spell_manager=spell_manager,
            astar_grid=astar_grid,
            grid=grid,
            logger=logger,
            service=service,
            character_state=char_state,
        )
        hud = Hud(logger=logger)
        job_parser = JobParser(service=service, logger=logger)
        hud_sys = HudSystem(
            hud=hud,
            image_manager=image_manager,
            character_state=char_state,
            service=service,
            controller=controller,
            object_searcher=object_searcher,
            capturer=self.capturer,
            logger=logger,
            job_parser=job_parser,
        )
        user = UserService.get_current_user(service)
        core_walker_sys = CoreWalkerSystem(
            hud_sys=hud_sys,
            logger=logger,
            map_state=MapState(),
            character_state=char_state,
            controller=controller,
            image_manager=image_manager,
            object_searcher=object_searcher,
            animation_manager=animation_manager,
            capturer=self.capturer,
            service=service,
            user=user,
        )
        fight_system = FightSystem(
            ia_brute_sys=ia_brute,
            core_walker_system=core_walker_sys,
            animation_manager=animation_manager,
            hud_sys=hud_sys,
            astar_grid=astar_grid,
            spell_manager=spell_manager,
            logger=logger,
            capturer=self.capturer,
            object_searcher=object_searcher,
            image_manager=image_manager,
            controller=controller,
            grid=grid,
            is_dead_event=Event(),
            service=service,
            is_in_fight_event=Event(),
        )
        self.connection = ConnectionSystem(
            fight_system=fight_system,
            hud_system=hud_sys,
            controller=controller,
            object_searcher=object_searcher,
            capturer=self.capturer,
            image_manager=image_manager,
            logger=logger,
            is_connected_event=Event(),
        )
        return super().setUp()

    def test_connect(self):
        assert self.connection.connect_character(self.capturer.capture()) is True

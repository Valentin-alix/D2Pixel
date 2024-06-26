from threading import Event, RLock
import traceback
from random import shuffle
from time import sleep
from typing import Callable

from EzreD2Shared.shared.schemas.map import MapSchema

from src.bots.dofus.antibot.afk_starter import AfkStarter
from src.bots.dofus.antibot.humanizer import Humanizer
from src.bots.dofus.chat.chat_system import ChatSystem
from src.bots.dofus.chat.sentence import FakeSentence
from src.bots.dofus.connection.connection_system import ConnectionSystem
from src.bots.dofus.elements.bank import BankSystem
from src.bots.dofus.elements.sale_hotel import SaleHotel, SaleHotelSystem
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
from src.bots.dofus.sub_area_farming.sub_area_farming_system import (
    SubAreaFarming,
    SubAreaFarmingSystem,
)
from src.bots.dofus.walker.buildings.bank_buildings import BankBuilding
from src.bots.dofus.walker.buildings.workshop_building import WorkshopBuilding
from src.bots.dofus.walker.core_walker_system import CoreWalkerSystem
from src.bots.dofus.walker.walker_system import WalkerSystem
from src.bots.modules.fighter.fighter import Fighter
from src.bots.modules.harvester.harvester import Harvester
from src.bots.modules.hdv.craft import Crafter
from src.bots.modules.hdv.hdv import Hdv
from src.bots.modules.hdv.sell import Seller
from src.common.loggers.bot_logger import BotLogger
from src.consts import DOFUS_WINDOW_SIZE
from src.exceptions import (
    CharacterIsStuckException,
    StoppedException,
    UnknowStateException,
)
from src.gui.signals.dofus_signals import BotSignals
from src.image_manager.animation import AnimationManager
from src.image_manager.screen_objects.icon_searcher import IconSearcher
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from src.states.character_state import CharacterState
from src.states.map_state import MapState
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller
from src.window_manager.organizer import Organizer, WindowInfo

DEFAULT_MODULES: list[str] = ["Hdv", "Fighter", "Harvester"]


class ModuleManager:
    def __init__(
        self,
        service: ServiceSession,
        window_info: WindowInfo,
        fake_sentence: FakeSentence,
        fighter_maps_time: dict[MapSchema, float],
        fighter_sub_areas_farming_ids: list[int],
        harvest_sub_areas_farming_ids: list[int],
        harvest_map_time: dict[MapSchema, float],
    ):
        self.window_info = window_info
        character_id = window_info.name.split(" - Dofus")[0]
        self.bot_signals = BotSignals()
        self.fake_sentence = fake_sentence
        self.service = service
        self.is_paused = Event()
        self.internal_pause = Event()
        self.is_playing = Event()
        self.is_connected = Event()
        self.is_dead = Event()
        self.not_in_fight = Event()
        self.action_lock = RLock()
        self.logger = BotLogger(character_id, self.bot_signals)

        self.organizer = Organizer(
            window_info=window_info,
            is_paused=self.is_paused,
            target_window_size=DOFUS_WINDOW_SIZE,
            logger=self.logger,
        )
        self.capturer = Capturer(
            action_lock=self.action_lock,
            organizer=self.organizer,
            is_paused=self.is_paused,
            window_info=self.window_info,
            logger=self.logger,
        )
        self.icon_searcher = IconSearcher(self.service)
        self.animation_manager = AnimationManager(capturer=self.capturer)
        self.object_searcher = ObjectSearcher(self.service)
        self.image_manager = ImageManager(self.capturer, self.object_searcher)
        grid = Grid(self.object_searcher)

        self.character_state = CharacterState(self.service, character_id)
        spell_manager = SpellManager(grid, self.service, self.character_state)

        self.controller = Controller(
            self.logger, window_info, self.is_paused, self.organizer, self.action_lock
        )
        spell_sys = SpellSystem(
            self.service,
            spell_manager,
            self.controller,
            self.capturer,
            self.object_searcher,
            self.image_manager,
            self.animation_manager,
            grid,
            self.logger,
        )
        astar_grid = AstarGrid(grid, self.logger)
        ldv_grid = LdvGrid(grid)
        ia_base_sys = IaBaseFightSystem(
            spell_sys,
            grid,
            ldv_grid,
            self.controller,
            self.animation_manager,
            self.service,
            self.character_state,
            self.logger,
        )
        ia_brute_sys = IaBruteFightSystem(
            ia_base_sys,
            spell_sys,
            spell_manager,
            astar_grid,
            grid,
            self.logger,
            self.service,
            self.character_state,
        )
        self.hud = Hud(logger=self.logger)
        self.job_parser = JobParser(service=self.service, logger=self.logger)
        self.hud_sys = HudSystem(
            hud=self.hud,
            image_manager=self.image_manager,
            character_state=self.character_state,
            service=self.service,
            controller=self.controller,
            object_searcher=self.object_searcher,
            capturer=self.capturer,
            logger=self.logger,
            job_parser=self.job_parser,
        )
        self.map_state = MapState()
        core_walker_sys = CoreWalkerSystem(
            self.hud_sys,
            self.logger,
            self.map_state,
            self.character_state,
            self.controller,
            self.image_manager,
            self.object_searcher,
            self.animation_manager,
            self.capturer,
            self.service,
        )
        fight_sys = FightSystem(
            ia_brute_sys,
            core_walker_sys,
            self.animation_manager,
            self.hud_sys,
            astar_grid,
            spell_manager,
            self.logger,
            self.capturer,
            self.object_searcher,
            self.image_manager,
            self.controller,
            grid,
            self.is_dead,
            self.service,
            self.not_in_fight,
        )
        walker_sys = WalkerSystem(
            fight_sys,
            self.hud_sys,
            self.logger,
            self.map_state,
            self.character_state,
            self.controller,
            self.image_manager,
            self.object_searcher,
            self.animation_manager,
            self.capturer,
            self.service,
        )

        self.connection_sys = ConnectionSystem(
            fight_sys,
            self.hud_sys,
            self.controller,
            self.object_searcher,
            self.capturer,
            self.image_manager,
            self.logger,
            self.is_connected,
            self.is_dead,
        )
        bank_building = BankBuilding(
            core_walker_sys,
            self.logger,
            self.controller,
            self.image_manager,
            self.service,
        )
        workshop_building = WorkshopBuilding(
            core_walker_sys,
            self.logger,
            self.controller,
            self.image_manager,
            self.service,
        )
        sale_hotel = SaleHotel(self.logger)
        sale_hotel_sys = SaleHotelSystem(
            core_walker_sys,
            sale_hotel,
            self.controller,
            self.capturer,
            self.object_searcher,
            self.icon_searcher,
            self.logger,
            self.image_manager,
            self.service,
            self.character_state,
        )
        bank_sys = BankSystem(
            bank_building,
            self.object_searcher,
            self.capturer,
            self.image_manager,
            self.icon_searcher,
            self.controller,
            self.service,
            core_walker_sys,
            self.character_state,
        )
        self.chat_sys = ChatSystem(self.controller, self.logger, self.fake_sentence)
        self.afk_starter = AfkStarter(
            self.connection_sys,
            self.controller,
            self.character_state,
            self.service,
            self.is_paused,
            self.is_playing,
            self.is_connected,
        )
        self.humanizer = Humanizer(self.chat_sys, self.is_connected, self.is_playing)

        crafter = Crafter(
            self.hud_sys,
            bank_sys,
            self.logger,
            self.image_manager,
            self.object_searcher,
            self.capturer,
            self.controller,
            workshop_building,
            self.service,
            self.character_state,
        )
        seller = Seller(
            self.service,
            self.character_state,
            sale_hotel_sys,
            self.hud_sys,
            bank_sys,
            self.logger,
            self.controller,
            self.capturer,
            self.image_manager,
        )
        self.hdv = Hdv(self.service, self.character_state, crafter, seller, self.logger)

        sub_area_farming = SubAreaFarming(self.service, self.character_state)
        sub_area_farming_sys = SubAreaFarmingSystem(
            self.service, core_walker_sys, self.character_state, self.logger
        )

        self.fighter = Fighter(
            self.service,
            self.character_state,
            sub_area_farming,
            sub_area_farming_sys,
            core_walker_sys,
            self.hud_sys,
            fight_sys,
            bank_sys,
            self.connection_sys,
            self.controller,
            self.object_searcher,
            self.capturer,
            self.image_manager,
            self.logger,
            fighter_maps_time,
            fighter_sub_areas_farming_ids,
        )

        self.harvester = Harvester(
            self.service,
            self.character_state,
            sub_area_farming_sys,
            sub_area_farming,
            self.connection_sys,
            walker_sys,
            self.hud_sys,
            bank_sys,
            self.controller,
            self.object_searcher,
            self.capturer,
            self.image_manager,
            self.logger,
            harvest_sub_areas_farming_ids,
            harvest_map_time,
        )

        self.modules: dict[str, Callable[..., None]] = {
            "Hdv": self.hdv.run_hdv,
            "Fighter": self.fighter.run_fighter,
            "Harvester": self.harvester.run_harvest,
        }

    def stop_bot(self):
        self.bot_signals.is_stopping_bot.emit(True)
        if self.is_playing.is_set():
            self.is_paused.set()
            while self.is_playing.is_set():
                self.logger.info("Waiting for stopped bot")
                sleep(0.5)
        self.bot_signals.is_stopping_bot.emit(False)

    def run_bot(self, name_modules: list[str] = DEFAULT_MODULES):
        self.stop_bot()

        self.is_paused.clear()
        self.is_playing.set()

        self.map_state.reset_map_state()

        if len(name_modules) == 0:
            return

        modules: list[tuple[str, Callable[..., None]]] = [
            (name, action)
            for name, action in self.modules.items()
            if name in name_modules
        ]
        shuffle(modules)
        try:
            self.afk_starter.run_afk_in_game()
            self.humanizer.run_humanizer()
            self.hud_sys.clean_interface(self.capturer.capture())
            while True:
                for name, action in modules:
                    self.bot_signals.playing_action.emit(name)
                    action()
        except StoppedException:
            self.logger.info("Stopped bot.")
        except (UnknowStateException, CharacterIsStuckException):
            self.logger.error(traceback.format_exc())
            self.connection_sys.deblock_character()
            return self.run_bot(name_modules)
        finally:
            self.logger.info("Bot terminated.")
            self.is_playing.clear()

import traceback
from enum import StrEnum
from random import shuffle
from threading import Event, RLock
from time import sleep
from typing import Callable

from D2Shared.shared.schemas.equipment import ReadEquipmentSchema
from D2Shared.shared.schemas.recipe import RecipeSchema
from D2Shared.shared.schemas.stat import BaseLineSchema, StatSchema
from D2Shared.shared.schemas.user import ReadUserSchema
from src.bots.dofus.antibot.humanizer import Humanizer
from src.bots.dofus.chat.chat_system import ChatSystem
from src.bots.dofus.chat.sentence import FakeSentence
from src.bots.dofus.connection.connection_system import ConnectionSystem
from src.bots.dofus.elements.bank import BankSystem
from src.bots.dofus.elements.sale_hotel import SaleHotel, SaleHotelSystem
from src.bots.dofus.elements.smithmagic_workshop import SmithMagicWorkshop
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
from src.bots.modules.fm.fm import Fm
from src.bots.modules.fm.fm_analyser import FmAnalyser
from src.bots.modules.harvester.harvester import Harvester
from src.bots.modules.hdv.craft.craft import Crafter
from src.bots.modules.hdv.hdv import Hdv
from src.bots.modules.hdv.sell import Seller
from src.common.loggers.bot_logger import BotLogger
from src.consts import DOFUS_WINDOW_SIZE
from src.exceptions import StoppedException
from src.gui.signals.app_signals import AppSignals
from src.gui.signals.bot_signals import BotSignals
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


class FarmingAction(StrEnum):
    HDV = "Hdv"
    FIGHTER = "Fighter"
    HARVESTER = "Harvester"


DEFAULT_FARMING_ACTIONS: list[FarmingAction] = [
    FarmingAction.HDV,
    FarmingAction.HARVESTER,
]


class Bot:
    def __init__(
        self,
        character_id: str,
        service: ServiceSession,
        fake_sentence: FakeSentence,
        window_info: WindowInfo,
        user: ReadUserSchema,
        fighter_maps_time: dict[int, float],
        fighter_sub_areas_farming_ids: list[int],
        harvest_sub_areas_farming_ids: list[int],
        harvest_map_time: dict[int, float],
        app_signals: AppSignals,
    ) -> None:
        self.fighter_maps_time = fighter_maps_time
        self.fighter_sub_areas_farming_ids = fighter_sub_areas_farming_ids
        self.harvest_sub_areas_farming_ids = harvest_sub_areas_farming_ids
        self.harvest_map_time = harvest_map_time
        self.character_id = character_id
        self.service = service
        self.window_info = window_info
        self.fake_sentence = fake_sentence
        self.user = user
        self.bot_signals = BotSignals()
        self.is_paused_event = Event()
        self.is_paused_internal_event = Event()
        self.is_playing_event = Event()
        self.is_connected_event = Event()
        self.is_dead_event = Event()
        self.is_in_fight_event = Event()
        self.action_lock = RLock()
        self.app_signals = app_signals
        self.logger = BotLogger(character_id, self.bot_signals)
        self.character_state = CharacterState(self.service, character_id)

        self._is_init_bot: bool = False

    def _init_bot(self):
        if self._is_init_bot:
            self.logger.info("already initialized bot")
            return
        self._is_init_bot = True
        self.organizer = Organizer(
            window_info=self.window_info,
            is_paused_event=self.is_paused_event,
            target_window_size=DOFUS_WINDOW_SIZE,
            logger=self.logger,
        )
        self.capturer = Capturer(
            action_lock=self.action_lock,
            organizer=self.organizer,
            is_paused_event=self.is_paused_event,
            window_info=self.window_info,
            logger=self.logger,
        )
        self.icon_searcher = IconSearcher(logger=self.logger, service=self.service)
        self.animation_manager = AnimationManager(
            logger=self.logger, capturer=self.capturer
        )
        self.object_searcher = ObjectSearcher(logger=self.logger, service=self.service)
        self.image_manager = ImageManager(self.capturer, self.object_searcher)
        grid = Grid(self.logger, self.object_searcher)

        self.character_state = CharacterState(self.service, self.character_id)
        spell_manager = SpellManager(grid, self.service, self.character_state)

        self.controller = Controller(
            self.logger,
            self.window_info,
            self.is_paused_event,
            self.organizer,
            self.action_lock,
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
            spell_manager,
            self.object_searcher,
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
            self.user,
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
            self.is_dead_event,
            self.service,
            self.is_in_fight_event,
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
            self.user,
        )

        self.connection_sys = ConnectionSystem(
            fight_sys,
            self.hud_sys,
            self.controller,
            self.object_searcher,
            self.capturer,
            self.image_manager,
            self.logger,
            self.app_signals,
            self.is_connected_event,
            self.is_paused_internal_event,
            self.is_playing_event,
            self.is_paused_event,
            self.is_in_fight_event,
            self.action_lock,
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
            self.logger,
        )
        self.chat_sys = ChatSystem(self.controller, self.logger, self.fake_sentence)
        self.humanizer = Humanizer(
            self.chat_sys, self.is_connected_event, self.is_playing_event, self.user
        )

        self.crafter = Crafter(
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
        self.hdv = Hdv(
            self.service, self.character_state, self.crafter, seller, self.logger
        )

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
            self.fighter_maps_time,
            self.fighter_sub_areas_farming_ids,
            self.user,
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
            self.harvest_sub_areas_farming_ids,
            self.harvest_map_time,
            self.user,
        )

        self.smithmagic_workshop = SmithMagicWorkshop()
        self.fm_analyser = FmAnalyser(
            self.logger, self.service, self.smithmagic_workshop
        )
        self.fm = Fm(
            self.bot_signals,
            self.controller,
            self.service,
            self.fm_analyser,
            self.logger,
            self.smithmagic_workshop,
            self.capturer,
        )

        self.modules: dict[str, Callable[..., None]] = {
            "Hdv": self.hdv.run,
            "Fighter": self.fighter.run,
            "Harvester": self.harvester.run,
        }

    def _stop_bot(self):
        if self.is_playing_event.is_set():
            self.is_paused_event.set()
            while self.is_playing_event.is_set():
                self.logger.info("Waiting for stopped bot")
                sleep(0.3)
            self.is_paused_event.clear()

    def stop_bot(self):
        self.bot_signals.is_stopping_bot.emit(True)
        self._stop_bot()
        self.bot_signals.is_stopping_bot.emit(False)

    def run_action(self, func: Callable) -> None:
        self._init_bot()

        self.bot_signals.is_stopping_bot.emit(True)
        self._stop_bot()
        self.is_paused_event.clear()
        self.is_playing_event.set()
        self.bot_signals.is_stopping_bot.emit(False)

        self.map_state.reset_map_state()

        try:
            func()
        except StoppedException:
            self.logger.info("Stopped bot.")
        except Exception:
            self.logger.error(traceback.format_exc())
        finally:
            self.logger.info("Bot terminated.")
            self.is_playing_event.clear()
            self.humanizer.stop_timers()
            self.bot_signals.terminated_bot.emit()
            self.bot_signals.is_stopping_bot.emit(False)

    def run_craft(self, recipes: list[RecipeSchema]):
        self.logger.info("Starting crafter")
        self.run_action(lambda: self.crafter.run_crafter(recipes))

    def run_fm(
        self,
        lines: list[BaseLineSchema],
        exo_stat: StatSchema | None,
        equipment: ReadEquipmentSchema | None = None,
    ):
        self.logger.info("Starting fm")
        self.run_action(lambda: self.fm.run(lines, exo_stat, equipment))

    def run_farming(self, farming_actions: list[str]):
        def _run_farming(_farming_actions: list[str]):
            if len(_farming_actions) == 0:
                return

            modules: list[tuple[str, Callable[..., None]]] = [
                (name, action)
                for name, action in self.modules.items()
                if name in _farming_actions
            ]
            shuffle(modules)
            self.humanizer.run_humanizer()
            self.hud_sys.clean_interface(self.capturer.capture())
            while not self.is_paused_event.is_set():
                for name, action in modules:
                    self.bot_signals.playing_action.emit(name)
                    try:
                        action()
                    except StoppedException:
                        raise
                    except Exception:
                        self.logger.error(traceback.format_exc())
                        self.connection_sys.deblock_character()
                sleep(1)

        self.logger.info("Starting farming")
        self.run_action(lambda: _run_farming(farming_actions))

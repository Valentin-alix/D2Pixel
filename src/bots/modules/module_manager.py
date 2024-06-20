import traceback
from random import shuffle
from time import sleep
from typing import Callable

from EzreD2Shared.shared.schemas.map import MapSchema

from src.bots.dofus.antibot.afk_starter import AfkStarter
from src.bots.dofus.antibot.humanizer import Humanizer
from src.bots.modules.fighter.fighter import Fighter
from src.bots.modules.harvester.harvester import Harvester
from src.bots.modules.hdv.hdv import Hdv
from src.exceptions import (
    CharacterIsStuckException,
    StoppedException,
    UnknowStateException,
)
from src.gui.signals.dofus_signals import DofusSignals
from src.window_manager.organizer import WindowInfo

DEFAULT_MODULES: list[str] = ["Hdv", "Fighter", "Harvester"]


class ModuleManager(Harvester, Fighter, Hdv, Humanizer, AfkStarter):
    bot_signals: DofusSignals

    def __init__(
        self,
        window_info: WindowInfo,
        fighter_maps_time: dict[MapSchema, float],
        fighter_sub_areas_farming_ids: list[int],
        harvest_sub_areas_farming_ids: list[int],
        harvest_map_time: dict[MapSchema, float],
    ):
        self.bot_signals = DofusSignals()
        super().__init__(
            window_info=window_info,
            bot_signals=self.bot_signals,
            harvest_sub_areas_farming_ids=harvest_sub_areas_farming_ids,
            harvest_map_time=harvest_map_time,
            fighter_maps_time=fighter_maps_time,
            fighter_sub_areas_farming_ids=fighter_sub_areas_farming_ids,
        )
        self.modules: dict[str, Callable[..., None]] = {
            "Hdv": self.run_hdv,
            "Fighter": self.run_fighter,
            "Harvester": self.run_harvest,
        }

    def stop_bot(self):
        self.bot_signals.is_stopping_bot.emit(True)
        if self.is_playing:
            self.is_paused = True
            while self.is_playing:
                self.log_info("Waiting for stopped bot")
                sleep(0.5)
        self.bot_signals.is_stopping_bot.emit(False)

    def run_bot(self, name_modules: list[str] = DEFAULT_MODULES):
        self.stop_bot()

        self.is_paused = False
        self.is_playing = True

        self.reset_map_state()

        if len(name_modules) == 0:
            return

        modules: list[tuple[str, Callable[..., None]]] = [
            (name, action)
            for name, action in self.modules.items()
            if name in name_modules
        ]
        shuffle(modules)
        try:
            self.run_afk_in_game()
            self.run_humanizer()
            self.clean_interface(self.capture())
            while True:
                for name, action in modules:
                    self.bot_signals.playing_action.emit(name)
                    action()
        except StoppedException:
            self.log_info("Stopped bot.")
        except (UnknowStateException, CharacterIsStuckException):
            self.log_error(traceback.format_exc())
            self.deblock_character()
            return self.run_bot(name_modules)
        finally:
            self.log_info("Bot terminated.")
            self.is_playing = False

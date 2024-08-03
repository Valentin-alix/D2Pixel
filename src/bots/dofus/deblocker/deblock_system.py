import traceback
from dataclasses import dataclass
from logging import Logger
from threading import Event, Thread
from time import sleep

from D2Shared.shared.consts.object_configs import ObjectConfigs
from src.bots.dofus.connection.connection_system import (
    ConnectionSystem,
    has_internet_connection,
)
from src.bots.dofus.fight.fight_system import FightSystem
from src.bots.dofus.hud.hud_system import Hud, HudSystem
from src.exceptions import StoppedException
from src.gui.signals.app_signals import AppSignals
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.window_manager.capturer import Capturer


@dataclass
class DeblockSystem:
    logger: Logger
    app_signals: AppSignals
    is_paused_internal_event: Event
    is_connected_event: Event
    capturer: Capturer
    hud: Hud
    hud_system: HudSystem
    object_searcher: ObjectSearcher
    connection_system: ConnectionSystem
    fight_system: FightSystem

    def is_blocked_character(self) -> bool:
        """check if character has any interface open or is not in game

        Returns:
            bool: is_blocked
        """
        img = self.capturer.capture()
        if not self.object_searcher.get_position(img, ObjectConfigs.in_game):
            return True

        for config in self.hud.close_interface_configs:
            if self.object_searcher.get_position(img, config):
                return True

        return False

    def deblock_character(self, retry: int = 15) -> None:
        self.logger.info("En train de débloquer le bot...")
        if retry <= 0:
            self.logger.info("Fail to deblock character, restarting...")
            pause_thread = Thread(target=self.connection_system.pause_bot, daemon=True)
            pause_thread.start()
            self.is_paused_internal_event.wait()
            self.app_signals.need_restart.emit()
            self.is_connected_event.wait()
            return self.deblock_character()

        while not has_internet_connection():
            self.logger.info("En attente d'une connexion internet...")
            sleep(1)
        try:
            img = self.capturer.capture()
            img, connected = self.connection_system.connect_character(img)
            if not connected:
                self.logger.info("Toujours pas connecté au jeu.")
                sleep(1)
                return self.deblock_character(retry - 1)
            elif self.object_searcher.get_position(img, ObjectConfigs.Fight.in_fight):
                img, _ = self.fight_system.play_fight()
        except StoppedException:
            raise
        except Exception:
            self.logger.error(traceback.format_exc())
            sleep(1)
            return self.deblock_character(retry - 1)
        self.hud_system.clean_interface(self.capturer.capture())
        self.logger.info("Bot débloqué.")

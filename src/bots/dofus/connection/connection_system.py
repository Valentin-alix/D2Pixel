import socket
from dataclasses import dataclass
from logging import Logger
from threading import Event, RLock
from time import sleep

import numpy

from D2Shared.shared.consts.object_configs import ObjectConfigs
from src.bots.dofus.fight.fight_system import FightSystem
from src.bots.dofus.hud.hud_system import HudSystem
from src.gui.signals.app_signals import AppSignals
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller


def has_internet_connection(host="8.8.8.8", port=53, timeout=3) -> bool:
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


@dataclass
class ConnectionSystem:
    fight_system: FightSystem
    hud_system: HudSystem
    controller: Controller
    object_searcher: ObjectSearcher
    capturer: Capturer
    image_manager: ImageManager
    logger: Logger
    app_signals: AppSignals
    is_connected_event: Event
    is_paused_internal_event: Event
    is_playing_event: Event
    is_paused_event: Event
    is_in_fight_event: Event
    action_lock: RLock

    def pause_bot(self):
        while True:
            if not self.is_playing_event.is_set() or self.is_paused_event.is_set():
                return
            if not self.is_in_fight_event.is_set():
                break
            self.logger.info("En attente que le bot ne soit plus en combat...")
            sleep(0.5)
        self.is_paused_internal_event.set()
        with self.action_lock:
            self.logger.info("Bot mis en pause.")
            self.is_connected_event.clear()
            self.controller.kill_window()
            while True:
                if not self.is_paused_internal_event.is_set():
                    break
                if self.is_paused_event.is_set():
                    break
                sleep(0.5)

    def connect_character(self, img: numpy.ndarray) -> tuple[numpy.ndarray, bool]:
        """return false if not connected"""
        self.logger.info("Connecting character")
        if (
            self.object_searcher.get_position(img, ObjectConfigs.Fight.grave)
            is not None
        ):
            img = self.fight_system.on_dead_character(img)
        else:
            self.logger.info("Clean interface")
            img = self.hud_system.clean_interface(img)

        if self.object_searcher.get_position(img, ObjectConfigs.in_game) is not None:
            self.logger.info("Est en jeu.")
            self.is_connected_event.set()
            return img, True
        pos_launcher_info = self.object_searcher.get_position(
            img, ObjectConfigs.Connection.launcher
        )
        if pos_launcher_info is not None:
            self.logger.info("A trouvé le bouton de connection au launcher.")
            self.controller.click(pos_launcher_info[0])
            pos_infos = self.image_manager.wait_multiple_or_template(
                [ObjectConfigs.Connection.play, ObjectConfigs.in_game]
            )
            if pos_infos is not None:
                img = pos_infos[3]
                if pos_infos[2] == ObjectConfigs.in_game:
                    self.is_connected_event.set()
                    return img, True

        pos_play_info = self.object_searcher.get_position(
            img, ObjectConfigs.Connection.play
        )
        if pos_play_info is not None:
            self.logger.info("A trouvé le bouton jouer.")
            self.controller.click(pos_play_info[0])
            in_game_info = self.image_manager.wait_on_screen(ObjectConfigs.in_game)
            if in_game_info is not None:
                self.is_connected_event.set()
                return in_game_info[2], True

        self.logger.info("Toujours pas connecté.")
        return img, False

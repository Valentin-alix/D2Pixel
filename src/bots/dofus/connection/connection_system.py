import socket
import traceback
from logging import Logger
from threading import Event
from time import sleep

import numpy

from D2Shared.shared.consts.object_configs import ObjectConfigs
from src.bots.dofus.fight.fight_system import FightSystem
from src.bots.dofus.hud.hud_system import HudSystem
from src.exceptions import (
    StoppedException,
)
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


class ConnectionSystem:
    def __init__(
        self,
        fight_system: FightSystem,
        hud_system: HudSystem,
        controller: Controller,
        object_searcher: ObjectSearcher,
        capturer: Capturer,
        image_manager: ImageManager,
        logger: Logger,
        is_connected: Event,
    ) -> None:
        self.object_searcher = object_searcher
        self.capturer = capturer
        self.fight_system = fight_system
        self.controller = controller
        self.image_manager = image_manager
        self.logger = logger
        self.is_connected = is_connected
        self.hud_system = hud_system

    def connect_character(self, img: numpy.ndarray) -> tuple[numpy.ndarray, bool]:
        """return false if not connected"""
        if (
            self.object_searcher.get_position(img, ObjectConfigs.Fight.grave)
            is not None
        ):
            img = self.fight_system.on_dead_character(img)
        else:
            img = self.hud_system.clean_interface(img)

        if self.object_searcher.get_position(img, ObjectConfigs.in_game) is not None:
            self.logger.info("Est en jeu.")
            self.is_connected.set()
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
                    self.is_connected.set()
                    return img, True

        pos_play_info = self.object_searcher.get_position(
            img, ObjectConfigs.Connection.play
        )
        if pos_play_info is not None:
            self.logger.info("A trouvé le button jouer.")
            self.controller.click(pos_play_info[0])
            in_game_info = self.image_manager.wait_on_screen(ObjectConfigs.in_game)
            if in_game_info is not None:
                self.is_connected.set()
                return in_game_info[2], True

        self.logger.info("Toujours pas connecté.")
        return img, False

    def deblock_character(self):
        self.logger.info("En train de débloquer le bot...")
        while not has_internet_connection():
            self.logger.info("En attente d'une connexion internet...")
            sleep(1)
        try:
            img = self.capturer.capture()
            img, connected = self.connect_character(img)
            if not connected:
                self.logger.info("Toujours pas connecté au jeu.")
                return self.deblock_character()
            elif self.object_searcher.get_position(img, ObjectConfigs.Fight.in_fight):
                img, _ = self.fight_system.play_fight()
        except StoppedException:
            raise
        except Exception:
            self.logger.error(traceback.format_exc())
            return self.deblock_character()
        self.hud_system.clean_interface(self.capturer.capture())
        self.logger.info("Bot débloqué.")

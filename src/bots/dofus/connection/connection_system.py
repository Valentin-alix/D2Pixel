import socket
import traceback
from threading import Event
from time import sleep

import numpy
from EzreD2Shared.shared.consts.object_configs import ObjectConfigs

from src.bots.dofus.fight.fight_system import FightSystem
from src.exceptions import (
    CharacterIsStuckException,
    StoppedException,
    UnknowStateException,
)


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
    except socket.error as ex:
        print(ex)
        return False


class ConnectionSystem(FightSystem):
    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.is_connected: Event = Event()

    def connect_character(self, img: numpy.ndarray) -> tuple[numpy.ndarray, bool]:
        """return false if not connected"""
        img = self.clean_interface(img)
        if self.get_position(img, ObjectConfigs.in_game) is not None:
            self.log_info("Is in game")
            self.is_connected.set()
            return img, True
        pos_launcher_info = self.get_position(img, ObjectConfigs.Connection.launcher)
        if pos_launcher_info is not None:
            self.log_info("Found Launcher Connection Button")
            self.click(pos_launcher_info[0])
            pos_infos = self.wait_multiple_or_template(
                [ObjectConfigs.Connection.play, ObjectConfigs.in_game]
            )
            if pos_infos is not None:
                img = pos_infos[3]
                if pos_infos[2] == ObjectConfigs.in_game:
                    self.is_connected.set()
                    return img, True

        pos_play_info = self.get_position(img, ObjectConfigs.Connection.play)
        if pos_play_info is not None:
            self.log_info("Found Play Character Button")
            self.click(pos_play_info[0])
            in_game_info = self.wait_on_screen(ObjectConfigs.in_game)
            if in_game_info is not None:
                self.is_connected.set()
                return in_game_info[2], True

        self.log_info("Still not connected")
        return img, False

    def deblock_character(self):
        self.log_info("Deblocking character...")
        while not has_internet_connection():
            self.log_info("Waiting for connection to be available...")
            sleep(2)
        try:
            img = self.capture()
            img, connected = self.connect_character(img)
            if not connected:
                self.log_info("Still not connected")
                return self.deblock_character()
            if self.is_dead:
                self.on_dead_character(img)
            elif self.get_position(img, ObjectConfigs.Fight.in_fight):
                img, _ = self.play_fight()
        except StoppedException:
            raise
        except (UnknowStateException, CharacterIsStuckException):
            self.log_error(traceback.format_exc())
            return self.deblock_character()
        self.clean_interface(self.capture())
        self.log_info("Character deblocked")

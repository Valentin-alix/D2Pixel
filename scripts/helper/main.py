import logging
import os
import sys
from logging import Logger
from threading import Event, Lock
from time import sleep


sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from D2Shared.shared.utils.randomizer import pick_random_weighted_time
from src.window_manager.window_searcher import (
    get_ankama_window_info,
)
from D2Shared.shared.consts.adaptative.positions import EMPTY_POSITION
from src.bots.ankama.ankama_launcher import AnkamaLauncher
from src.gui.signals.app_signals import AppSignals
from src.services.session import ServiceSession


if __name__ == "__main__":
    temp = pick_random_weighted_time(0.3, 1)
    print(temp)
    sys.exit()
    logger = Logger("root")
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    is_paused = Event()
    ank_window = get_ankama_window_info(logger=logger)
    assert ank_window is not None
    service = ServiceSession(logger, AppSignals())
    launcher = AnkamaLauncher(
        window_info=ank_window, logger=logger, service=service, dc_lock=Lock()
    )
    launcher.controller.click(EMPTY_POSITION)

    sleep(5)
    text = launcher.controller.get_selected_text()
    print(text)

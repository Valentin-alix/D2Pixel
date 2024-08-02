import logging
import os
import sys
from logging import Logger

sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from src.window_manager.window_searcher import get_windows_by_process_and_name

if __name__ == "__main__":
    logger = Logger("root")
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    # service = ServiceSession(logger, AppSignals())
    # launcher = AnkamaLauncher(logger, service)
    # dofus_windows = launcher.connect_all()

    windows_ankama = get_windows_by_process_and_name("Ankama Launcher.exe")
    logger.info(f"Found ankama windows : {windows_ankama}")

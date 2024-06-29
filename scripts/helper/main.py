from logging import Logger
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from src.bots.ankama.ankama_launcher import AnkamaLauncher
from src.services.session import ServiceSession
from src.gui.signals.app_signals import AppSignals

if __name__ == "__main__":
    logger = Logger("root")
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    service = ServiceSession(logger, AppSignals())
    launcher = AnkamaLauncher(logger, service)
    dofus_windows = launcher.connect_all()

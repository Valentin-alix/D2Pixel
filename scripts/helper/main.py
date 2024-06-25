from logging import Logger
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from src.bots.ankama.ankama_launcher import AnkamaLauncher
from src.services.session import ServiceSession


if __name__ == "__main__":
    logger = Logger("root")
    service = ServiceSession(logger)
    launcher = AnkamaLauncher(logger, service)
    dofus_windows = launcher.connect_all()

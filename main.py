import sys

from src.gui.app import Application
from src.gui.main_window import MainWindow
from src.gui.signals.app_signals import AppSignals
from src.loggers.app_logger import AppLogger
from src.services.session import ServiceSession

if __name__ == "__main__":
    app_signals = AppSignals()
    app_logger = AppLogger(app_signals)
    service = ServiceSession(app_logger, app_signals)

    app = Application(sys.argv)
    main_window = MainWindow(app.TITLE, app_logger, service, app_signals)
    sys.exit(app.exec_())

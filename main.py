import sys

from PyQt5.QtWidgets import QDialog
from src.consts import ENV_PATH
from src.gui.pages.login import LoginModal
from src.common.loggers.app_logger import AppLogger
from src.gui.app import Application, MainWindow
from src.gui.components.loaders import SplashScreen
from src.gui.signals.app_signals import AppSignals
from src.services.session import ServiceSession
from dotenv import get_key

if __name__ == "__main__":
    app_signals = AppSignals()
    app_logger = AppLogger(app_signals)
    service = ServiceSession(app_logger, app_signals)

    app = Application(sys.argv)
    if get_key(ENV_PATH, "USERNAME") is None or get_key(ENV_PATH, "PASSWORD") is None:
        input_dialog = LoginModal()
        if input_dialog.exec_() != QDialog.Accepted:
            sys.exit()
    splash = SplashScreen()
    splash.show()
    main_window = MainWindow(app_logger, service, app_signals)
    splash.finish(main_window)
    sys.exit(app.exec_())

import asyncio
import sys

from qasync import QEventLoop

from src.common.loggers.app_logger import AppLogger
from src.gui.app import Application
from src.gui.main_window import MainWindow
from src.gui.signals.app_signals import AppSignals
from src.services.client_service import ClientService

if __name__ == "__main__":
    app = Application(sys.argv)
    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)

    app_signals = AppSignals()
    app_logger = AppLogger(app_signals)
    client_service = ClientService(app_signals, app_logger)
    main_window = MainWindow(app.TITLE, app_logger, client_service, app_signals)
    main_window.show()

    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())

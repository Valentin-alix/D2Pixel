from contextlib import contextmanager
from logging import Logger

from dotenv import get_key
from PyQt5.QtCore import QEventLoop, QTimer
from requests import Response, Session
from requests.auth import HTTPBasicAuth

from src.consts import ENV_PATH
from src.gui.signals.app_signals import AppSignals


class ServiceSession:
    def __init__(self, logger: Logger, app_signals: AppSignals) -> None:
        self.app_signals = app_signals
        self.logger = logger

    def __handle_error(self, rep: Response, *args, **kwargs):
        def retry_request():
            with self.logged_session() as session:
                rep.request.prepare_auth(session.auth)
                return session.send(rep.request, verify=False)

        if rep.status_code in [500]:
            self.logger.error("Erreur du serveur interne.")
        elif rep.status_code in [400]:
            self.logger.error(f"Erreur : {rep.content}")
        elif rep.status_code == 401:
            self.logger.error("Erreur d'authentification.")
            if "/login/" not in rep.url:
                self.app_signals.login_failed.emit()
                event_loop = QEventLoop()
                self.app_signals.login_success.connect(event_loop.quit)
                QTimer.singleShot(0, event_loop.exec_)  # don't block main thread
                return retry_request()
        return rep

    @contextmanager
    def logged_session(self):
        try:
            session = Session()
            session.hooks["response"].append(self.__handle_error)
            session.auth = HTTPBasicAuth(
                get_key(ENV_PATH, "USERNAME") or "", get_key(ENV_PATH, "PASSWORD") or ""
            )
            yield session
        finally:
            session.close()

    @contextmanager
    def unlogged_session(self):
        try:
            session = Session()
            session.hooks["response"].append(self.__handle_error)
            yield session
        finally:
            session.close()

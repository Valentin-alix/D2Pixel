from contextlib import contextmanager
from requests import Response, Session
from src.common.loggers.app_logger import AppLogger
from requests.auth import HTTPBasicAuth
from dotenv import get_key

from src.consts import ENV_PATH
from src.exceptions import AuthenticationError
from src.gui.signals.app_signals import AppSignals


class ServiceSession:
    def __init__(self, logger: AppLogger, app_signals: AppSignals) -> None:
        self.app_signals = app_signals
        self.logger = logger

    def __handle_error(self, rep: Response, *args, **kwargs):
        if rep.status_code != 200:
            self.logger.error(f"{rep.status_code} {rep.json()}")

    @contextmanager
    def logged_session(self):
        try:
            session = Session()
            session.hooks["response"].append(self.__handle_error)
            if (username := get_key(ENV_PATH, "USERNAME")) is None or (
                password := get_key(ENV_PATH, "PASSWORD")
            ) is None:
                raise AuthenticationError()

            session.auth = HTTPBasicAuth(username, password)
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

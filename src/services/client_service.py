from logging import Logger

from dotenv import get_key
from httpx import AsyncClient, BasicAuth, Response
from PyQt5.QtCore import QEventLoop, QTimer

from src.consts import ENV_PATH
from src.gui.signals.app_signals import AppSignals


class ClientService:
    def __init__(self, app_signals: AppSignals, logger: Logger) -> None:
        self.logger = logger
        self.app_signals = app_signals
        self._refresh_credentials()
        self._refresh_session()

    def _refresh_credentials(self):
        self.username = get_key(ENV_PATH, "USERNAME") or ""
        self.password = get_key(ENV_PATH, "PASSWORD") or ""

    def _refresh_session(self):
        auth = BasicAuth(self.username, self.password)
        self.session = AsyncClient(
            auth=auth,
            event_hooks={
                "response": [self._log_response],
            },
        )

    async def _log_response(self, response: Response) -> Response:
        if response.status_code == 401:
            self.logger.error("Erreur d'authentification.")
            if "/login/" not in response.url.fragment:
                self.app_signals.login_failed.emit()
                event_loop = QEventLoop()
                self.app_signals.login_success.connect(event_loop.quit)
                QTimer.singleShot(0, event_loop.exec_)  # don't block main thread

                # refresh headers of request
                self._refresh_credentials()
                self._refresh_session()
                response.request.headers["Authorization"] = f"Basic {self.session.auth}"
                # retry request
                new_response = await self.session.send(response.request)
                return new_response

        if response.status_code != 200:
            self.logger.error(f"{response.status_code} : {await response.aread()}")
            response.raise_for_status()

        return response

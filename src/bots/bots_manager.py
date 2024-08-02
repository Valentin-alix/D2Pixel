from collections import defaultdict
from logging import Logger

from D2Shared.shared.schemas.user import ReadUserSchema
from src.bots.ankama.ankama_launcher import AnkamaLauncher
from src.bots.dofus.antibot.playtime_manager import PlayTimeManager
from src.bots.dofus.chat.sentence import FakeSentence
from src.bots.dofus.connection.connection_manager import ConnectionManager
from src.bots.modules.bot import Bot
from src.gui.signals.app_signals import AppSignals
from src.services.session import ServiceSession
from src.window_manager.organizer import (
    WindowInfo,
    relink_windows_hwnd,
)


class BotsManager:
    def __init__(
        self,
        logger: Logger,
        service: ServiceSession,
        app_signals: AppSignals,
        user: ReadUserSchema,
    ) -> None:
        self.app_signals = app_signals
        self.service = service
        self.fake_sentence = FakeSentence()
        self.logger = logger
        self.user = user
        self.bots_by_id: dict[str, Bot] = {}
        self.ankama_launcher = AnkamaLauncher(logger, service)
        self.connection_manager = ConnectionManager(
            logger, service, user, self.ankama_launcher, self.bots_by_id, app_signals
        )
        self.playtime_manager = PlayTimeManager(user, self.connection_manager)
        self.fighter_map_time: dict[int, float] = defaultdict(lambda: 0)
        self.fighter_sub_area_farming_ids: list[int] = []

        self.harvest_map_time: dict[int, float] = defaultdict(lambda: 0)
        self.harvest_sub_area_farming_ids: list[int] = []
        self.app_signals.need_restart.connect(self._on_need_restart)

    def connect_all(self):
        self.ankama_launcher.launch_dofus_games()
        dofus_windows = self.connection_manager.connect_all_dofus_account()
        self._setup_bots(dofus_windows)

    def _on_need_restart(self) -> None:
        self.connect_all()

    def _setup_bots(self, dofus_windows: list[WindowInfo]):
        untreated_ids: list[str] = list(self.bots_by_id.keys())
        for window in dofus_windows:
            character_id = window.name.split(" - Dofus")[0]
            if character_id in untreated_ids:
                untreated_ids.remove(character_id)
            if (bot := self.bots_by_id.get(character_id)) is None:
                bot = Bot(
                    character_id,
                    self.service,
                    self.fake_sentence,
                    window,
                    self.user,
                    self.fighter_map_time,
                    self.fighter_sub_area_farming_ids,
                    self.harvest_sub_area_farming_ids,
                    self.harvest_map_time,
                    self.app_signals,
                )
            else:
                relink_windows_hwnd(bot.window_info, dofus_windows)
            bot.is_connected_event.set()
            self.bots_by_id[character_id] = bot

        for _id in untreated_ids:
            del self.bots_by_id[_id]

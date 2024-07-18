from collections import defaultdict
from logging import Logger

from D2Shared.shared.schemas.user import ReadUserSchema
from src.bots.ankama.ankama_launcher import AnkamaLauncher, relink_windows_dofus_hwnd
from src.bots.dofus.chat.sentence import FakeSentence
from src.bots.modules.bot import Bot
from src.gui.signals.app_signals import AppSignals
from src.services.session import ServiceSession
from src.window_manager.organizer import (
    WindowInfo,
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
        self.ankama_launcher: None | AnkamaLauncher = None
        self.bots: dict[str, Bot] = {}
        self.fighter_map_time: dict[int, float] = defaultdict(lambda: 0)
        self.fighter_sub_area_farming_ids: list[int] = []

        self.harvest_map_time: dict[int, float] = defaultdict(lambda: 0)
        self.harvest_sub_area_farming_ids: list[int] = []

    def connect_all(self):
        self.app_signals.is_connecting.emit(True)
        if self.ankama_launcher is None:
            self.ankama_launcher = AnkamaLauncher(self.logger, self.service, self.user)
            self.ankama_launcher.run_playtime_planner(self.bots)
        dofus_windows = self.ankama_launcher.connect_all()
        self._setup_bots(dofus_windows)
        self.app_signals.is_connecting.emit(False)

    def _setup_bots(self, dofus_windows: list[WindowInfo]):
        for window in dofus_windows:
            character_id = window.name.split(" - Dofus")[0]
            if (bot := self.bots.get(character_id)) is None:
                bot = Bot(
                    character_id,
                    self.service,
                    self.fake_sentence,
                    self.user,
                    self.fighter_map_time,
                    self.fighter_sub_area_farming_ids,
                    self.harvest_sub_area_farming_ids,
                    self.harvest_map_time,
                )
            relink_windows_dofus_hwnd(bot, dofus_windows)
            bot.init_bot(window)
            bot.is_connected.set()
            self.bots[character_id] = bot

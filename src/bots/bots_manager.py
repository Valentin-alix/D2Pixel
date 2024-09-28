from collections import defaultdict
from dataclasses import dataclass, field
from logging import Logger
from threading import Lock

from D2Shared.shared.schemas.user import ReadUserSchema
from src.bots.ankama.ankama_launcher import AnkamaLauncher, get_or_launch_ankama_window
from src.bots.dofus.chat.sentence import FakeSentence
from src.bots.dofus.connection.connection_manager import ConnectionManager
from src.bots.modules.bot import Bot
from src.gui.signals.app_signals import AppSignals
from src.services.session import ServiceSession
from src.window_manager.organizer import (
    relink_windows_hwnd,
)
from src.window_manager.window_info import WindowInfo


@dataclass
class BotsManager:
    logger: Logger
    service: ServiceSession
    app_signals: AppSignals
    user: ReadUserSchema

    fake_sentence: FakeSentence = field(default_factory=FakeSentence, init=False)
    bots_by_id: dict[str, Bot] = field(default_factory=lambda: {}, init=False)
    dc_lock: Lock = field(default_factory=Lock, init=False)
    ankama_launcher: AnkamaLauncher | None = field(default=None, init=False)
    connection_manager: ConnectionManager | None = field(default=None, init=False)
    fighter_map_time: dict[int, float] = field(
        default_factory=lambda: defaultdict(lambda: 0), init=False
    )
    fighter_sub_area_farming_ids: list[int] = field(
        default_factory=lambda: [], init=False
    )
    harvest_map_time: dict[int, float] = field(
        default_factory=lambda: defaultdict(lambda: 0), init=False
    )
    harvest_sub_area_farming_ids: list[int] = field(
        default_factory=lambda: [], init=False
    )

    def __post_init__(self):
        self.app_signals.need_restart.connect(self.connect_all)

    def connect_all(self):
        if self.ankama_launcher is None:
            ankama_window = get_or_launch_ankama_window(self.logger)
            self.ankama_launcher = AnkamaLauncher(
                ankama_window, self.logger, self.service, self.dc_lock
            )
        if self.connection_manager is None:
            self.connection_manager = ConnectionManager(
                logger=self.logger,
                service=self.service,
                user=self.user,
                dc_lock=self.dc_lock,
            )

        self.ankama_launcher.launch_dofus_games()
        dofus_windows = self.connection_manager.connect_all_dofus_account()
        self._setup_bots(dofus_windows)

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
                    self.dc_lock,
                )
            else:
                relink_windows_hwnd(bot.window_info, dofus_windows)
            bot.is_connected_event.set()
            self.bots_by_id[character_id] = bot

        for _id in untreated_ids:
            del self.bots_by_id[_id]

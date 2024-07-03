from collections import defaultdict
from logging import Logger


from D2Shared.shared.schemas.user import ReadUserSchema
from src.bots.ankama.ankama_launcher import AnkamaLauncher
from src.bots.dofus.chat.sentence import FakeSentence
from src.bots.modules.module_manager import ModuleManager
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
        self.module_managers: list[ModuleManager] = []
        self.app_signals = app_signals
        self.service = service
        self.fake_sentence = FakeSentence()
        self.logger = logger
        self.app_signals.is_connecting_bots.emit(True)
        self.user = user
        self.ankama_launcher = AnkamaLauncher(self.logger, self.service, self.user)
        dofus_windows = self.ankama_launcher.connect_all()
        self._setup_farmers(dofus_windows)

        self.app_signals.is_connecting_bots.emit(False)

    def _setup_farmers(self, dofus_windows: list[WindowInfo]):
        fighter_map_time: dict[int, float] = defaultdict(lambda: 0)
        fighter_sub_area_farming_ids: list[int] = []

        harvest_map_time: dict[int, float] = defaultdict(lambda: 0)
        harvest_sub_area_farming_ids: list[int] = []

        for window in dofus_windows:
            module_manager = ModuleManager(
                self.service,
                window,
                self.fake_sentence,
                fighter_map_time,
                fighter_sub_area_farming_ids,
                harvest_sub_area_farming_ids,
                harvest_map_time,
                self.user,
            )
            module_manager.is_connected.set()
            self.module_managers.append(module_manager)

        self.ankama_launcher.run_playtime_planner(self.module_managers)

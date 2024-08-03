from dataclasses import dataclass

import schedule

from D2Shared.shared.schemas.user import ReadUserSchema
from src.bots.dofus.connection.connection_manager import ConnectionManager
from src.utils.scheduler import run_continuously


@dataclass
class PlayTimeManager:
    user: ReadUserSchema
    connection_manager: ConnectionManager

    def __post_init__(self):
        self.run()

    def run(self) -> None:
        for range_hour_playtime in self.user.config_user.ranges_hour_playtime:
            schedule.every().day.at(range_hour_playtime.end_time.strftime("%H:%M")).do(
                self.connection_manager.pause_bots
            )
            schedule.every().day.at(
                range_hour_playtime.start_time.strftime("%H:%M")
            ).do(self.connection_manager.resume_bots)

        run_continuously()

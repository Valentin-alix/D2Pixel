import schedule

from D2Shared.shared.schemas.user import ReadUserSchema
from src.bots.dofus.connection.connection_manager import ConnectionManager
from src.common.scheduler import run_continuously


class PlayTimeManager:
    def __init__(
        self, user: ReadUserSchema, connection_manager: ConnectionManager
    ) -> None:
        self.user = user
        self.connection_manager = connection_manager
        self.run()

    def run(self) -> None:
        for range_hour_playtime in self.user.config_user.ranges_hour_playtime:
            schedule.every().day.at(range_hour_playtime.end_time.strftime("%H:%M")).do(
                lambda: self.connection_manager.pause_bots()
            )
            schedule.every().day.at(
                range_hour_playtime.start_time.strftime("%H:%M")
            ).do(lambda: self.connection_manager.resume_bots())

        run_continuously()

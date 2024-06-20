import atexit
from time import perf_counter, sleep

from EzreD2Shared.shared.consts.adaptative.positions import EMPTY_POSITION

from src.bots.dofus.connection.connection_system import ConnectionSystem
from src.bots.dofus.dofus_bot import DofusBot
from src.services.character import CharacterService

START_MIN_AFK_TIME = 60 * 60 * 3

INACTIVITY_TIME_LIMIT = 60 * 10


class AfkStarter(ConnectionSystem, DofusBot):
    def run_afk_in_game(self) -> None:
        """Handle afk time to avoid antibot, afk the first 5 hour of the bot"""

        def update_character_time_spent(init_time: float):
            self.character.time_spent += perf_counter() - init_time
            self.character = CharacterService.update_character(self.character)

        if self.character.lvl > 1 or self.character.time_spent > START_MIN_AFK_TIME:
            return

        time_since_click: float = 0
        init_time = perf_counter()
        atexit.register(lambda: update_character_time_spent(init_time))

        while (
            ((curr_time := perf_counter()) - init_time < START_MIN_AFK_TIME)
            and not self.is_paused
            and self.is_playing
            and self.is_connected.is_set()
        ):
            if curr_time - time_since_click > INACTIVITY_TIME_LIMIT:
                self.click(EMPTY_POSITION)
                time_since_click = curr_time
            sleep(1)

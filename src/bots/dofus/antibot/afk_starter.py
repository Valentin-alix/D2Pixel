import atexit
from threading import Event
from time import perf_counter, sleep

from D2Shared.shared.consts.adaptative.positions import EMPTY_POSITION

from src.bots.dofus.connection.connection_system import ConnectionSystem
from src.consts import START_MIN_AFK_TIME
from src.services.character import CharacterService
from src.services.session import ServiceSession
from src.states.character_state import CharacterState
from src.window_manager.controller import Controller

INACTIVITY_TIME_LIMIT = 60 * 10


class AfkStarter:
    def __init__(
        self,
        connection_sys: ConnectionSystem,
        controller: Controller,
        character_state: CharacterState,
        service: ServiceSession,
        is_paused: Event,
        is_playing: Event,
        is_connected: Event,
    ) -> None:
        self.connection_sys = connection_sys
        self.controller = controller
        self.character_state = character_state
        self.service = service
        self.is_paused = is_paused
        self.is_playing = is_playing
        self.is_connected = is_connected

    def run_afk_in_game(self) -> None:
        """Handle afk time to avoid antibot, afk the first 5 hour of the bot"""

        def update_character_time_spent(init_time: float):
            self.character_state.character.time_spent += perf_counter() - init_time
            self.character_state.character = CharacterService.update_character(
                self.service, self.character_state.character
            )

        if (
            self.character_state.character.lvl > 1
            or self.character_state.character.time_spent > START_MIN_AFK_TIME
        ):
            return

        time_since_click: float = 0
        init_time = perf_counter()
        atexit.register(lambda: update_character_time_spent(init_time))

        while (
            ((curr_time := perf_counter()) - init_time < START_MIN_AFK_TIME)
            and not self.is_paused.is_set()
            and self.is_playing.is_set()
            and self.is_connected.is_set()
        ):
            if curr_time - time_since_click > INACTIVITY_TIME_LIMIT:
                self.controller.click(EMPTY_POSITION)
                time_since_click = curr_time
            sleep(1)

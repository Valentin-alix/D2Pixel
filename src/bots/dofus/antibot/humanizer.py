import random
from dataclasses import dataclass, field
from threading import Event, Timer
from typing import Callable

from D2Shared.shared.schemas.user import ReadUserSchema
from src.bots.dofus.chat.chat_system import ChatSystem
from src.utils.time import convert_time_to_seconds


@dataclass
class Humanizer:
    chat_system: ChatSystem
    is_connected_event: Event
    is_playing_event: Event
    user: ReadUserSchema

    _timers: list[Timer] = field(default_factory=lambda: [], init=False)

    def run_random_action(self, func: Callable, time: float):
        """run funct in interval based on time randomized"""

        def run_func_regularly():
            if self.is_connected_event.is_set() and self.is_playing_event.is_set():
                func()
            timer = Timer(
                random.uniform(time * 0.2, time * 1.8),
                run_func_regularly,
            )
            self._timers.append(timer)
            timer.start()

        timer = Timer(
            random.uniform(time * 0.2, time * 1.8),
            run_func_regularly,
        )
        self._timers.append(timer)
        timer.start()

    def run_humanizer(self):
        self.run_random_action(
            self.chat_system.type_random_sentence,
            convert_time_to_seconds(self.user.config_user.time_between_sentence),
        )

    def stop_timers(self):
        for timer in self._timers:
            timer.cancel()

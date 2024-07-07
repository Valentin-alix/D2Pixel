import random
import threading
from typing import Callable

from D2Shared.shared.schemas.user import ReadUserSchema
from src.bots.dofus.chat.chat_system import ChatSystem
from src.common.time import convert_time_to_seconds


class Humanizer:
    def __init__(
        self,
        chat_system: ChatSystem,
        is_connected: threading.Event,
        is_playing: threading.Event,
        user: ReadUserSchema,
    ) -> None:
        self.chat_system = chat_system
        self.is_connected = is_connected
        self.is_playing = is_playing
        self.user = user
        self.timers: list[threading.Timer] = []

    def run_random_action(self, func: Callable, time: float):
        """run funct in interval based on time randomized"""

        def run_func_regularly():
            if self.is_connected.is_set() and self.is_playing.is_set():
                func()
            timer = threading.Timer(
                random.uniform(time * 0.2, time * 1.8),
                run_func_regularly,
            )
            self.timers.append(timer)
            timer.start()

        timer = threading.Timer(
            random.uniform(time * 0.2, time * 1.8),
            run_func_regularly,
        )
        self.timers.append(timer)
        timer.start()

    def run_humanizer(self):
        self.run_random_action(
            self.chat_system.type_random_sentence,
            convert_time_to_seconds(self.user.config_user.time_between_sentence),
        )

    def stop_timers(self):
        for timer in self.timers:
            timer.cancel()

import random
import threading
from typing import Callable

from src.bots.dofus.chat.chat_system import ChatSystem
from src.bots.dofus.connection.connection_system import ConnectionSystem

TIME_SENTENCE = 60 * 30


class Humanizer(ConnectionSystem, ChatSystem):
    def run_random_action(self, func: Callable, time: float):
        """run funct in interval based on time randomized"""

        def run_func_regularly():
            if self.is_connected.is_set() and self.is_playing:
                func()
            timer = threading.Timer(
                random.uniform(time * 0.2, time * 1.8),
                run_func_regularly,
            )
            timer.start()

        timer = threading.Timer(
            random.uniform(time * 0.2, time * 1.8),
            run_func_regularly,
        )
        timer.start()

    def run_humanizer(self):
        self.run_random_action(self.type_random_sentence, TIME_SENTENCE)

import unittest
from logging import Logger
from threading import Event, RLock

from src.bots.dofus.chat.chat_system import ChatSystem
from src.bots.dofus.chat.sentence import FakeSentence
from src.consts import DOFUS_WINDOW_SIZE
from src.window_manager.controller import Controller
from src.window_manager.organizer import Organizer
from tests.tests_system.utils import get_first_window_dofus


@unittest.skipIf((window := get_first_window_dofus()) is None, "")
class TestChatSystem(unittest.TestCase):
    chat: ChatSystem

    def setUp(self) -> None:
        assert window is not None
        logger = Logger("root")
        is_paused = Event()
        organizer = Organizer(
            window_info=window,
            is_paused_event=is_paused,
            target_window_width_height=DOFUS_WINDOW_SIZE,
            logger=logger,
        )
        action_lock = RLock()
        controller = Controller(
            logger=logger,
            window_info=window,
            is_paused_event=is_paused,
            organizer=organizer,
            action_lock=action_lock,
        )
        self.chat = ChatSystem(
            controller=controller, logger=logger, fake_sentence=FakeSentence()
        )
        return super().setUp()

    def test_random_sentence(self):
        for _ in range(5):
            self.chat.type_random_sentence()

    def test_write_chat(self):
        self.chat.write_chat("Salut à toutes et à tous")

    def test_clear_chat(self):
        self.chat.clear_chat()

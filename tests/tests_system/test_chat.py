import unittest

from src.bots.dofus.chat.chat_system import ChatSystem
from tests.tests_system.utils import get_base_params_system


@unittest.skipIf(get_base_params_system().get("window", None) is None, "")
class TestChatSystem(unittest.TestCase):
    chat: ChatSystem

    def setUp(self) -> None:
        self.chat = ChatSystem(**get_base_params_system())
        return super().setUp()

    def test_random_sentence(self):
        for _ in range(5):
            self.chat.type_random_sentence()

    def test_write_chat(self):
        self.chat.write_chat("Salut à toutes et à tous")

    def test_clear_chat(self):
        self.chat.clear_chat()

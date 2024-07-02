from logging import Logger
from D2Shared.shared.consts.adaptative.positions import CHAT_TEXT_POSITION

from src.bots.dofus.chat.sentence import FakeSentence
from src.window_manager.controller import Controller


class ChatSystem:
    def __init__(
        self, controller: Controller, logger: Logger, fake_sentence: FakeSentence
    ) -> None:
        self.controller = controller
        self.logger = logger
        self.fake_sentence = fake_sentence

    def type_random_sentence(self):
        random_sentence = self.fake_sentence.get_random_sentence()
        self.logger.info(f"Écris des mots aléatoire dans le chat : {random_sentence}.")
        self.write_chat(random_sentence)

    def write_chat(self, text: str):
        self.controller.send_text(text, pos=CHAT_TEXT_POSITION)
        self.controller.void_click()

    def clear_chat(self):
        self.logger.info("Nettoie le chat.")
        self.write_chat("/clear")

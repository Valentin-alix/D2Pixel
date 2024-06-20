from EzreD2Shared.shared.consts.adaptative.positions import CHAT_TEXT_POSITION

from src.bots.dofus.chat.sentence import FakeSentence
from src.bots.dofus.dofus_bot import DofusBot


class ChatSystem(DofusBot, FakeSentence):
    def type_random_sentence(self):
        random_sentence = self.get_random_sentence()
        self.log_info(f"Typing random word in chat : {random_sentence}")
        self.write_chat(random_sentence)

    def write_chat(self, text: str):
        self.send_text(text, pos=CHAT_TEXT_POSITION)
        self.void_click()

    def clear_chat(self):
        self.log_info("Clear chat")
        self.write_chat("/clear")

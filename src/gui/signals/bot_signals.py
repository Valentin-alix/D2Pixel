from PyQt5.QtCore import QObject, pyqtSignal


class BotSignals(QObject):
    playing_action = pyqtSignal(str)
    is_stopping_bot = pyqtSignal(bool)
    log_info = pyqtSignal(object)
    disconnected_bot = pyqtSignal()

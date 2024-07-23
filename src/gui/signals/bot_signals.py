from PyQt5.QtCore import QObject, pyqtSignal


class BotSignals(QObject):
    playing_action = pyqtSignal(str)
    is_stopping_bot = pyqtSignal(bool)
    log_info = pyqtSignal(object)
    terminated_bot = pyqtSignal()
    fm_new_line_value = pyqtSignal(object)
    fm_new_count_achieved = pyqtSignal(int)

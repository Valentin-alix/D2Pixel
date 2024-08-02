from PyQt5.QtCore import QObject, pyqtSignal


class AppSignals(QObject):
    connected_bots = pyqtSignal(object)
    is_connecting = pyqtSignal(bool)
    on_close = pyqtSignal()
    log_info = pyqtSignal(object)
    login_failed = pyqtSignal()
    login_success = pyqtSignal()
    need_restart = pyqtSignal()

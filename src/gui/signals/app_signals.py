from PyQt5.QtCore import QObject, pyqtSignal


class AppSignals(QObject):
    bots_initialized = pyqtSignal(object)
    is_connecting_bots = pyqtSignal(bool)
    on_close = pyqtSignal()

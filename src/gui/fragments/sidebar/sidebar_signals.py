from PyQt5.QtCore import QObject, pyqtSignal


class SideBarSignals(QObject):
    clicked_bot = pyqtSignal(int)

import os

from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtWidgets import QSplashScreen, QWidget
from pyqtspinner import WaitingSpinner

from src.consts import ASSET_FOLDER_PATH


class Loading(WaitingSpinner):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(
            parent=parent,
            roundness=100.0,
            fade=80.0,
            radius=20,
            lines=100,
            line_length=15,
            line_width=10,
            speed=1.0,
            color=QColor(os.environ["QTMATERIAL_PRIMARYCOLOR"]),
        )


class SplashScreen(QSplashScreen):
    def __init__(self):
        super(QSplashScreen, self).__init__()
        pixmap = QPixmap(os.path.join(ASSET_FOLDER_PATH, "icons", "logo_safe_bot.png"))
        self.setPixmap(pixmap)

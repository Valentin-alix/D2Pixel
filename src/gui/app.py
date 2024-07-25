import ctypes
import os

from PyQt5.QtCore import (
    Qt,
)
from qasync import QApplication
from qt_material import apply_stylesheet

from src.consts import RESOURCE_FOLDER_PATH


class Application(QApplication):
    TITLE = "D2SafeBot"

    def __init__(self, argv) -> None:
        # authorize app to change icon of application
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "dofus.evoker_bot"
        )

        super().__init__(argv)
        self.setAttribute(Qt.ApplicationAttribute.AA_DisableWindowContextHelpButton)
        self.setApplicationName(self.TITLE)

        apply_stylesheet(
            self,
            theme="dark_yellow.xml",
            css_file=os.path.join(RESOURCE_FOLDER_PATH, "styles.qss"),
            invert_secondary=False,
        )

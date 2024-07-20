import os

from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import QAbstractButton, QPushButton, QToolButton

from src.consts import ASSET_FOLDER_PATH


class AbstractButton(
    QAbstractButton,
):
    def __init__(self, checkable: bool = False, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setCheckable(checkable)
        self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.setFocusPolicy(QtCore.Qt.NoFocus)


class PushButton(QPushButton, AbstractButton):
    def __init__(self, flat: bool = False, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setFlat(flat)


class ToolButton(QToolButton, AbstractButton): ...


class PushButtonIcon(PushButton):
    def __init__(
        self,
        filename: str | None = None,
        width: int | None = None,
        height: int | None = None,
        icon_size: int | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        if filename is not None:
            self.set_icon(filename)
        if icon_size is not None:
            self.setIconSize(QSize(icon_size, icon_size))
        if height is not None:
            self.setFixedHeight(height)
        if width is not None:
            self.setFixedWidth(width)

    def set_icon(self, filename: str):
        self.setIcon(QIcon(os.path.join(ASSET_FOLDER_PATH, "icons", filename)))


class ToolButtonIcon(ToolButton):
    def __init__(
        self,
        filename: str,
        width: int | None = None,
        height: int | None = None,
        icon_size: int | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.set_icon(filename)
        if height is not None:
            self.setFixedHeight(height)
        if width is not None:
            self.setFixedWidth(width)
        if icon_size is not None:
            self.setIconSize(QSize(icon_size, icon_size))

    def set_icon(self, filename):
        self.setIcon(QIcon(os.path.join(ASSET_FOLDER_PATH, "icons", filename)))

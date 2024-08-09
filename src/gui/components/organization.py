from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QStyledItemDelegate,
    QVBoxLayout,
)


DEFAULT_SPACING: int = 4
DEFAULT_MARGINS: tuple[int, int, int, int] = (0, 0, 0, 0)


class VerticalLayout(QVBoxLayout):
    def __init__(
        self,
        space: int = DEFAULT_SPACING,
        margins: tuple[int, int, int, int] = DEFAULT_MARGINS,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.setSpacing(space)
        self.setContentsMargins(*margins)


class HorizontalLayout(QHBoxLayout):
    def __init__(
        self,
        space: int = DEFAULT_SPACING,
        margins: tuple[int, int, int, int] = DEFAULT_MARGINS,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.setSpacing(space)
        self.setContentsMargins(*margins)


class GridLayout(QGridLayout):
    def __init__(
        self,
        space: int = DEFAULT_SPACING,
        margins: tuple[int, int, int, int] = DEFAULT_MARGINS,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.setSpacing(space)
        self.setContentsMargins(*margins)


class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignCenter

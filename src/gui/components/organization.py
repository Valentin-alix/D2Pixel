from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLayout,
    QSpacerItem,
    QStyledItemDelegate,
    QVBoxLayout,
)


class Layout(QLayout):
    def set_default_space(
        self, space: int = 0, margins: tuple[int, int, int, int] = (0, 0, 0, 0)
    ):
        self.setSpacing(space)
        self.setContentsMargins(*margins)

    def clear_list(self, proportion: float = 1, clear_spacer=False):
        for i in reversed(range(int(self.count() * proportion))):
            if (item := self.itemAt(i)) is not None:
                if clear_spacer and isinstance(item, QSpacerItem):
                    self.removeItem(item)

                if (item_widget := item.widget()) is not None:
                    item_widget.deleteLater()


DEFAULT_SPACING = 4
DEFAULT_MARGINS = (0, 0, 0, 0)


class VerticalLayout(QVBoxLayout, Layout):
    def __init__(
        self,
        space: int = DEFAULT_SPACING,
        margins: tuple[int, int, int, int] = DEFAULT_MARGINS,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.set_default_space(space, margins)


class HorizontalLayout(QHBoxLayout, Layout):
    def __init__(
        self,
        space: int = DEFAULT_SPACING,
        margins: tuple[int, int, int, int] = DEFAULT_MARGINS,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.set_default_space(space, margins)


class GridLayout(QGridLayout, Layout):
    def __init__(
        self,
        space: int = DEFAULT_SPACING,
        margins: tuple[int, int, int, int] = DEFAULT_MARGINS,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.set_default_space(space, margins)


class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignCenter

from src.gui.components.buttons import PushButtonIcon
from src.gui.components.organization import HorizontalLayout
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QSizePolicy, QWidget

HEADER_HEIGHT = 32  # standard height


class HeaderItem(PushButtonIcon):
    def __init__(self, filename: str | None = None, *args, **kwargs) -> None:
        super().__init__(
            height=HEADER_HEIGHT,
            icon_size=16,
            checkable=False,
            flat=True,
            filename=filename,
            *args,
            **kwargs,
        )


class Header(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.installEventFilter(self)
        self.parent = parent
        self.is_full_screen = False

        self.setAttribute(
            Qt.WA_StyledBackground, True
        )  # to apply style to whole widget
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(HEADER_HEIGHT)

        self.main_layout = HorizontalLayout(space=4, margins=(0, 0, 0, 0))
        self.main_layout.setAlignment(Qt.AlignRight)
        self.setLayout(self.main_layout)

        self.minimize_button = HeaderItem(filename="minimize.svg", parent=self)
        self.minimize_button.clicked.connect(self.on_minimize)
        self.main_layout.addWidget(self.minimize_button)

        self.maximize_button = HeaderItem(parent=self)
        self.maximize_button.clicked.connect(self.on_resize)
        self.main_layout.addWidget(self.maximize_button)

        if self.is_full_screen:
            self.maximize_button.set_icon("restore.png")
        else:
            self.maximize_button.set_icon("maximize.svg")

        self.quit_button = HeaderItem(filename="close.svg", parent=self)
        self.quit_button.setProperty("class", "danger")
        self.quit_button.clicked.connect(self.on_quit)
        self.main_layout.addWidget(self.quit_button)

    def on_minimize(self):
        self.parent.showMinimized()

    def on_resize(self):
        if not self.is_full_screen:
            self.parent.showFullScreen()
            self.maximize_button.set_icon("restore.png")
        else:
            self.parent.showNormal()
            self.maximize_button.set_icon("maximize.svg")
        self.is_full_screen = not self.is_full_screen

    def on_quit(self):
        self.parent.close()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseMove:
            if event.buttons() == Qt.LeftButton:
                self.parent.move(
                    self.parent.pos() + event.globalPos() - self.drag_position
                )
                self.drag_position = event.globalPos()
                event.accept()
                return True
        elif (
            event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton
        ):
            self.drag_position = event.globalPos()
            event.accept()
            return True
        return super().eventFilter(obj, event)

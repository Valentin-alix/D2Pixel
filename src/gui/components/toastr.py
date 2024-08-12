import logging
from typing import cast
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QLabel, QWidget

from src.gui.components.buttons import LocalPushButton, PushButtonIcon


class QToaster(QtWidgets.QFrame):
    current_toastr: "QToaster | None" = None

    label: QLabel
    closeButton: LocalPushButton

    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        QtWidgets.QHBoxLayout(self)

        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

        self.setAutoFillBackground(True)
        self.setFrameShape(self.Box)

        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_ani = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity")
        # we have a parent, install an eventFilter so that when it's resized
        # the notification will be correctly moved to the right corner
        self.parent().installEventFilter(self)

        self.opacity_ani.setStartValue(0.0)
        self.opacity_ani.setEndValue(1.0)
        self.opacity_ani.setDuration(100)
        self.opacity_ani.finished.connect(self.checkClosed)

        self.corner = QtCore.Qt.TopLeftCorner
        self.margin = 10

    def checkClosed(self):
        # if we have been fading out, we're closing the notification
        if self.opacity_ani.direction() == self.opacity_ani.Backward:
            self.close()

    def restore(self):
        # this is a "helper function", that can be called from mouseEnterEvent
        # and when the parent widget is resized. We will not close the
        # notification if the mouse is in or the parent is resized
        self.timer.stop()
        # also, stop the animation if it's fading out...
        self.opacity_ani.stop()
        # ...and restore the opacity
        if self.parent():
            self.opacity_effect.setOpacity(1)
        else:
            self.setWindowOpacity(1)

    def hide(self):
        # start hiding
        self.opacity_ani.setDirection(self.opacity_ani.Backward)
        self.opacity_ani.setDuration(500)
        self.opacity_ani.start()

    def eventFilter(self, source, event):
        if source == self.parent() and event.type() == QtCore.QEvent.Resize:
            self.opacity_ani.stop()
            parent = cast(QtWidgets.QFrame, self.parent())
            parent_rect = parent.rect()
            geo = self.geometry()
            if self.corner == QtCore.Qt.TopLeftCorner:
                geo.moveTopLeft(
                    parent_rect.topLeft() + QtCore.QPoint(self.margin, self.margin)
                )
            elif self.corner == QtCore.Qt.TopRightCorner:
                geo.moveTopRight(
                    parent_rect.topRight() + QtCore.QPoint(-self.margin, self.margin)
                )
            elif self.corner == QtCore.Qt.BottomRightCorner:
                geo.moveBottomRight(
                    parent_rect.bottomRight()
                    + QtCore.QPoint(-self.margin, -self.margin)
                )
            else:
                geo.moveBottomLeft(
                    parent_rect.bottomLeft() + QtCore.QPoint(self.margin, -self.margin)
                )
            self.setGeometry(geo)
            self.restore()
            self.timer.start()
        return super(QToaster, self).eventFilter(source, event)

    def enterEvent(self, event):
        self.restore()

    def leaveEvent(self, event):
        self.timer.start()

    def closeEvent(self, event):
        self.deleteLater()
        QToaster.current_toastr = None

    def resizeEvent(self, event):
        super(QToaster, self).resizeEvent(event)
        # if you don't set a stylesheet, you don't need any of the following!
        self.clearMask()


def show_message(
    parent: QWidget,
    message: str,
    level: int,
    corner=QtCore.Qt.TopLeftCorner,
    margin: int = 5,
    timeout: int = 5000,
):
    if QToaster.current_toastr is not None:
        QToaster.current_toastr.close()

    parent = parent.window()

    toastr = QToaster(parent)
    QToaster.current_toastr = toastr
    toastr.setMinimumWidth(120)

    label_icon = QtWidgets.QLabel()
    toastr.layout().addWidget(label_icon)

    match level:
        case logging.WARNING:
            icon = toastr.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_MessageBoxWarning
            )
        case logging.ERROR:
            icon = toastr.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_MessageBoxCritical
            )
        case logging.CRITICAL:
            icon = toastr.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_MessageBoxCritical
            )
        case _:
            icon = toastr.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_MessageBoxInformation
            )

    size = toastr.style().pixelMetric(QtWidgets.QStyle.PM_SmallIconSize)
    label_icon.setPixmap(icon.pixmap(size))

    parent_rect = parent.rect()

    toastr.timer.setInterval(timeout)

    toastr.label = QtWidgets.QLabel(message)
    toastr.layout().addWidget(toastr.label)

    toastr.closeButton = PushButtonIcon("close.svg", width=20, height=20)
    toastr.closeButton.setProperty("class", "no-border")
    toastr.layout().addWidget(toastr.closeButton)
    toastr.closeButton.clicked.connect(toastr.close)

    toastr.timer.start()

    # raise the widget and adjust its size to the minimum
    toastr.raise_()
    toastr.adjustSize()

    toastr.corner = corner
    toastr.margin = margin

    geo = toastr.geometry()
    # now the widget should have the correct size hints, let's move it to the
    # right place
    if corner == QtCore.Qt.TopLeftCorner:
        geo.moveTopLeft(parent_rect.topLeft() + QtCore.QPoint(margin, margin))
    elif corner == QtCore.Qt.TopRightCorner:
        geo.moveTopRight(parent_rect.topRight() + QtCore.QPoint(-margin, margin))
    elif corner == QtCore.Qt.BottomRightCorner:
        geo.moveBottomRight(parent_rect.bottomRight() + QtCore.QPoint(-margin, -margin))
    else:
        geo.moveBottomLeft(parent_rect.bottomLeft() + QtCore.QPoint(margin, -margin))

    toastr.setGeometry(geo)
    toastr.show()
    toastr.opacity_ani.start()

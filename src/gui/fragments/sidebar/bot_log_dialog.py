import logging

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from src.bots.modules.bot import Bot
from src.gui.components.dialog import Dialog
from src.gui.components.organization import VerticalLayout


class BotLogDialog(Dialog):
    class LogsDelegate(QtWidgets.QStyledItemDelegate):
        def paint(self, painter, option, index):
            log_msg = index.data(QtCore.Qt.DisplayRole)
            log_type = index.data(QtCore.Qt.UserRole)
            font = option.font
            font.setBold(True)
            match log_type:
                case logging.DEBUG:
                    option.palette.setColor(QtGui.QPalette.Text, QtGui.QColor("white"))
                case logging.INFO:
                    option.palette.setColor(
                        QtGui.QPalette.Text, QtGui.QColor("lightblue")
                    )
                case logging.WARNING:
                    option.palette.setColor(QtGui.QPalette.Text, QtGui.QColor("yellow"))
                case logging.ERROR:
                    option.palette.setColor(QtGui.QPalette.Text, QtGui.QColor("red"))
                case logging.CRITICAL:
                    option.palette.setColor(QtGui.QPalette.Text, QtGui.QColor("red"))
            painter.save()
            painter.setFont(font)
            painter.setPen(option.palette.color(QtGui.QPalette.Text))
            painter.drawText(option.rect, QtCore.Qt.AlignLeft, log_msg)
            painter.restore()

    def __init__(self, bot: Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.setWindowTitle(f"Logs de {bot.character_id}")
        self.resize(800, 300)
        self.log_box_layout = VerticalLayout()
        self.log_box_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.log_box_layout)

        self.list_logs = QListWidget()
        self.log_delegate = BotLogDialog.LogsDelegate()
        self.list_logs.setItemDelegate(self.log_delegate)

        self.log_box_layout.addWidget(self.list_logs)

        self.bot.bot_signals.log_info.connect(self.on_log_info)

    @pyqtSlot(object)
    def on_log_info(self, msg_with_type: tuple[int, str]):
        scrollbar = self.list_logs.verticalScrollBar()

        if self.list_logs.count() > 500:
            old_scroll_value = scrollbar.value()
            self.list_logs.takeItem(0)
            scrollbar.setValue(old_scroll_value)

        widget_item = QListWidgetItem(msg_with_type[1])
        widget_item.setData(Qt.UserRole, msg_with_type[0])
        self.list_logs.addItem(widget_item)
        if scrollbar.value() == scrollbar.maximum():
            self.list_logs.scrollToBottom()

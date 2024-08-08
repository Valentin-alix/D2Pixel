from abc import abstractmethod
from PyQt5.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QGroupBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QWidget,
)

from src.gui.components.organization import HorizontalLayout, VerticalLayout


class GroupListSignals(QObject):
    clicked_elem_queue = pyqtSignal(object)


class GroupList[T](QGroupBox):
    def __init__(self, elems: list[T], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.signals = GroupListSignals()
        self.setLayout(VerticalLayout())

        self.search_input_name_elem: str = ""
        self.elem_widget_by_name: dict[str, QListWidgetItem] = {}
        self.elems: list[T] = []
        self.setup_list_elems(elems)

    @abstractmethod
    def get_name_elem(self, elem: T) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_id_elem(self, elem: T) -> str | int:
        raise NotImplementedError

    def setup_list_elems(self, elems: list[T]) -> None:
        self.list_wid_elem = QListWidget()
        self.list_wid_elem.setLayoutMode(QListWidget.Batched)
        self.list_wid_elem.setBatchSize(10)
        self.list_wid_elem.setUniformItemSizes(True)
        for elem in elems:
            self.add_elem(elem)
        self.list_wid_elem.itemClicked.connect(self._on_click_elem_widget)
        self.layout().addWidget(self.list_wid_elem)

        bottom_widget = QWidget()
        bottom_widget.setLayout(HorizontalLayout())

        self.search_elem_edit = QLineEdit()
        self.search_elem_edit.textChanged.connect(self._on_search_elems)
        bottom_widget.layout().addWidget(self.search_elem_edit)

        self.layout().addWidget(bottom_widget)

    def add_elem(self, elem: T) -> None:
        self.elems.append(elem)
        elem_wid_item = QListWidgetItem(self.get_name_elem(elem))
        elem_wid_item.setData(Qt.UserRole, self.get_id_elem(elem))
        self.elem_widget_by_name[self.get_name_elem(elem)] = elem_wid_item
        self.list_wid_elem.addItem(elem_wid_item)

    def remove_elem(self, elem: T):
        self.elems.remove(elem)
        related_item = self.elem_widget_by_name.pop(self.get_name_elem(elem))
        row_index = self.list_wid_elem.row(related_item)
        self.list_wid_elem.takeItem(row_index)

    def filter_elems(self, search_input_elem: str):
        for elem in self.elems:
            related_item = self.elem_widget_by_name[self.get_name_elem(elem)]
            if (
                search_input_elem == ""
                or search_input_elem.casefold() in related_item.text().casefold()
            ):
                related_item.setHidden(False)
            else:
                related_item.setHidden(True)

    def on_refresh_elems(self, elems: list[T]):
        untreated_elems: dict[str, T] = {
            self.get_name_elem(_elem): _elem for _elem in elems
        }
        for curr_elem_name in self.elem_widget_by_name.keys():
            related_untreated_elem = untreated_elems.pop(curr_elem_name, None)
            if not related_untreated_elem:
                related_curr_elem = next(
                    _elem
                    for _elem in self.elems
                    if self.get_name_elem(_elem) == curr_elem_name
                )
                self.remove_elem(related_curr_elem)
                continue

        for elem in untreated_elems.values():
            self.add_elem(elem)

        self.filter_elems(self.search_input_name_elem)

    def _on_click_elem_widget(self, elem_widget: QListWidgetItem):
        elem_id = elem_widget.data(Qt.UserRole)
        related_elem: T = next(
            _elem for _elem in self.elems if self.get_id_elem(_elem) == elem_id
        )
        self.remove_elem(related_elem)
        self.signals.clicked_elem_queue.emit(related_elem)

    @pyqtSlot(str)
    def _on_search_elems(self, elem_name: str) -> None:
        self.search_input_name_elem = elem_name
        self.filter_elems(self.search_input_name_elem)

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
    def __init__(
        self, elems: list[T], is_lazy_loaded: bool = False, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.is_lazy_loaded = is_lazy_loaded
        self.signals = GroupListSignals()
        self.setLayout(VerticalLayout())

        self.input_search: str = ""
        self.widget_by_name: dict[str, QListWidgetItem] = {}
        self.elems_by_name: dict[str, T] = {}
        self.setup_list_elems(elems)

    @abstractmethod
    def get_name_elem(self, elem: T) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_widget_elem(self, elem: T) -> QWidget:
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

        search_elem_edit = QLineEdit()
        search_elem_edit.textChanged.connect(self._on_search_changed)
        bottom_widget.layout().addWidget(search_elem_edit)

        self.layout().addWidget(bottom_widget)

    def get_or_create_widget_item(self, elem: T) -> QListWidgetItem:
        if elem_wid_item := self.widget_by_name.get(self.get_name_elem(elem)):
            return elem_wid_item
        elem_wid_item = QListWidgetItem()
        elem_wid_item.setData(Qt.UserRole, self.get_name_elem(elem))
        elem_wid = self.get_widget_elem(elem)
        elem_wid_item.setSizeHint(elem_wid.sizeHint())
        self.list_wid_elem.addItem(elem_wid_item)
        self.list_wid_elem.setItemWidget(elem_wid_item, elem_wid)
        self.widget_by_name[self.get_name_elem(elem)] = elem_wid_item
        return elem_wid_item

    def add_elem(self, elem: T) -> None:
        self.elems_by_name[self.get_name_elem(elem)] = elem
        if not self.is_lazy_loaded:
            self.get_or_create_widget_item(elem)

    def remove_elem(self, elem: T):
        print(elem)
        print(self.get_name_elem(elem))
        self.elems_by_name.pop(self.get_name_elem(elem))
        related_item = self.widget_by_name.pop(self.get_name_elem(elem))
        row_index = self.list_wid_elem.row(related_item)
        self.list_wid_elem.takeItem(row_index)

    def filter_elems(self, search_input_elem: str):
        for elem in self.elems_by_name.values():
            if self.is_lazy_loaded:
                if (
                    len(search_input_elem) > 2
                    and search_input_elem.casefold()
                    in self.get_name_elem(elem).casefold()
                ):
                    related_widget = self.get_or_create_widget_item(elem)
                    related_widget.setHidden(False)
                elif related_widget := self.widget_by_name.get(
                    self.get_name_elem(elem)
                ):
                    related_widget.setHidden(True)
            else:
                related_widget = self.get_or_create_widget_item(elem)
                if (
                    search_input_elem == ""
                    or search_input_elem.casefold()
                    in self.get_name_elem(elem).casefold()
                ):
                    related_widget.setHidden(False)
                else:
                    related_widget.setHidden(True)

    def on_refresh_elems(self, elems: list[T]):
        untreated_elems: dict[str, T] = {
            self.get_name_elem(_elem): _elem for _elem in elems
        }
        for curr_elem_name in self.widget_by_name.keys():
            related_untreated_elem = untreated_elems.pop(curr_elem_name, None)
            if not related_untreated_elem:
                related_curr_elem = self.elems_by_name[curr_elem_name]
                self.remove_elem(related_curr_elem)
                continue

        for elem in untreated_elems.values():
            self.add_elem(elem)

        self.filter_elems(self.input_search)

    @pyqtSlot(object)
    def _on_click_elem_widget(self, item: QListWidgetItem):
        name = item.data(Qt.UserRole)
        elem = self.elems_by_name[name]
        self.signals.clicked_elem_queue.emit(elem)

    @pyqtSlot(str)
    def _on_search_changed(self, name: str) -> None:
        self.input_search = name
        self.filter_elems(self.input_search)

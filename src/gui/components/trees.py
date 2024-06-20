from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class TreeWidget(QTreeWidget):
    def __init__(self, json: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header().hide()
        self.deep_tree_from_message_dict(json, None, self)

    def deep_tree_from_message_dict(
        self,
        _values,
        parent: QTreeWidgetItem | None = None,
        base_qtree: QTreeWidget | None = None,
    ):
        if not isinstance(_values, dict):
            widget_item = QTreeWidgetItem([f"{_values}"])
            if parent is not None:
                parent.addChild(widget_item)
        else:
            for key, value in _values.items():
                if isinstance(value, dict):
                    widget_item = QTreeWidgetItem([f"{key}"])
                    self.deep_tree_from_message_dict(value, widget_item)
                elif isinstance(value, list):
                    widget_item = QTreeWidgetItem([f"{key}"])
                    for _value in value:
                        self.deep_tree_from_message_dict(_value, widget_item)
                else:
                    widget_item = QTreeWidgetItem([f"{key} = {value}"])
                if parent is not None:
                    parent.addChild(widget_item)
                elif base_qtree is not None:
                    base_qtree.addTopLevelItem(widget_item)

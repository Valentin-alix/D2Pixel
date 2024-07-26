from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QLabel, QWidget

from D2Shared.shared.schemas.character import CharacterSchema
from D2Shared.shared.schemas.sub_area import SubAreaSchema
from src.gui.components.combobox import CheckableComboBox
from src.gui.components.organization import HorizontalLayout, VerticalLayout
from src.services.character import CharacterService
from src.services.session import ServiceSession
from src.services.sub_area import SubAreaService


class FarmTab(QWidget):
    def __init__(
        self, service: ServiceSession, character: CharacterSchema, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.setLayout(VerticalLayout())
        self.service = service
        self.character = character
        self.combo_sub_areas: list[CheckableComboBox[SubAreaSchema]] = []
        self._set_sub_area_farmable()

    def _set_sub_area_farmable(self) -> None:
        sub_area_widg = QWidget()
        self.layout().addWidget(sub_area_widg)
        sub_area_layout = VerticalLayout()
        sub_area_layout.setAlignment(Qt.AlignHCenter)
        sub_area_widg.setLayout(sub_area_layout)

        title = QLabel()
        title.setText("Zones farmables")
        sub_area_layout.addWidget(title)

        list_sub_areas = QWidget()
        sub_area_layout.addWidget(list_sub_areas)
        h_layout = HorizontalLayout()
        list_sub_areas.setLayout(h_layout)

        all_sub_areas = SubAreaService.get_sub_areas(self.service)
        areas = sorted(
            set(elem.area for elem in all_sub_areas), key=lambda elem: elem.name
        )

        GROUP_COUNT: int = 8
        for index in range(0, len(areas), GROUP_COUNT):
            group_areas = QWidget()
            h_layout.addWidget(group_areas)
            group_form_layout = VerticalLayout()
            group_areas.setLayout(group_form_layout)

            for area in areas[index : index + GROUP_COUNT]:
                area_widg = QWidget()
                group_form_layout.addWidget(area_widg)

                form_l = QFormLayout()
                area_widg.setLayout(form_l)

                combo_sub = CheckableComboBox[SubAreaSchema](parent=self)
                self.combo_sub_areas.append(combo_sub)

                for sub_area in sorted(
                    [elem for elem in all_sub_areas if elem.area_id == area.id],
                    key=lambda elem: elem.name,
                ):
                    checked = sub_area in self.character.sub_areas
                    combo_sub.addItem(sub_area.name, sub_area, checked=checked)
                form_l.addRow(area.name, combo_sub)

    def on_save(self):
        new_sub_areas: list[SubAreaSchema] = [
            _elem for combo in self.combo_sub_areas for _elem in combo.currentData()
        ]
        if set(self.character.sub_areas) != set(new_sub_areas):
            self.character.sub_areas = new_sub_areas
            CharacterService.update_sub_areas(
                self.service,
                self.character.id,
                [elem.id for elem in self.character.sub_areas],
            )

from functools import partial

from pydantic import BaseModel, ConfigDict
from PyQt5.QtWidgets import QCheckBox, QComboBox, QLineEdit, QWidget

from D2Shared.shared.enums import CharacteristicEnum, ElemEnum
from D2Shared.shared.schemas.character import CharacterSchema
from D2Shared.shared.schemas.spell import SpellSchema
from src.gui.components.buttons import PushButtonIcon
from src.gui.components.organization import VerticalLayout
from src.gui.components.table import TableWidget
from src.services.session import ServiceSession


class SpellInfoEdits(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    name_edit: QLineEdit
    index_edit: QLineEdit
    elem_combo: QComboBox
    disenchantment_checkbox: QCheckBox
    boost_combo: QComboBox
    healing_checkbox: QCheckBox
    for_enemy_checkbox: QCheckBox
    ap_cost_edit: QLineEdit
    max_cast_edit: QLineEdit
    min_range_edit: QLineEdit
    range_edit: QLineEdit
    duration_boost_edit: QLineEdit
    boostable_range_checkbox: QCheckBox
    level_edit: QLineEdit


class GameplayTab(QWidget):
    def __init__(
        self, service: ServiceSession, character: CharacterSchema, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.spell_edits: dict[int, SpellInfoEdits] = {}
        self.service = service
        self.character = character
        self.setLayout(VerticalLayout())
        self.set_prefered_ia()
        self.init_spell_configs()

    def set_prefered_ia(self): ...

    def init_spell_configs(self) -> None:
        add_spell_btn = PushButtonIcon("add.svg")
        add_spell_btn.setCheckable(False)
        add_spell_btn.clicked.connect(lambda: self.add_spell())
        self.layout().addWidget(add_spell_btn)

        columns = [
            "Nom",
            "Index",
            "Élément",
            "Désenchante",
            "Boost",
            "Soigne",
            "Pour un enemi",
            "PA",
            "Max par tour",
            "Portée min",
            "Portée",
            "Durée de boost",
            "Portée Boostable",
            "LVL",
            "",
        ]
        self.spells_table = TableWidget(columns)
        self.layout().addWidget(self.spells_table)

        spells: list[SpellSchema] = self.character.spells
        for spell in spells:
            self.add_spell(spell)

    def add_spell(self, spell: SpellSchema | None = None):
        index = self.spells_table.table.rowCount()
        self.spells_table.table.setRowCount(index + 1)
        name_edit = QLineEdit()
        if spell:
            name_edit.setText(spell.name)
        self.spells_table.table.setCellWidget(index, 0, name_edit)

        index_edit = QLineEdit()
        if spell:
            index_edit.setText(str(spell.index))
        self.spells_table.table.setCellWidget(index, 1, index_edit)

        elem_combo = QComboBox()
        elem_combo.addItem("", None)
        for elem_option in ElemEnum:
            elem_combo.addItem(elem_option, elem_option)
        self.spells_table.table.setCellWidget(index, 2, elem_combo)
        if spell:
            elem_index = elem_combo.findData(spell.elem)
            elem_combo.setCurrentIndex(elem_index)

        disenchantment_checkbox = QCheckBox()
        if spell:
            disenchantment_checkbox.setChecked(spell.is_disenchantment)
        self.spells_table.table.setCellWidget(index, 3, disenchantment_checkbox)

        boost_combo = QComboBox()
        boost_combo.addItem("", None)
        for boost_option in CharacteristicEnum:
            boost_combo.addItem(boost_option, boost_option)
        self.spells_table.table.setCellWidget(index, 4, boost_combo)
        if spell:
            boost_index = boost_combo.findData(spell.boost_char)
            boost_combo.setCurrentIndex(boost_index)

        healing_checkbox = QCheckBox()
        self.spells_table.table.setCellWidget(index, 5, healing_checkbox)
        if spell:
            healing_checkbox.setChecked(spell.is_healing)

        for_enemy_checkbox = QCheckBox()
        self.spells_table.table.setCellWidget(index, 6, for_enemy_checkbox)
        if spell:
            for_enemy_checkbox.setChecked(spell.is_for_enemy)

        ap_cost_edit = QLineEdit()
        self.spells_table.table.setCellWidget(index, 7, ap_cost_edit)
        if spell:
            ap_cost_edit.setText(str(spell.ap_cost))

        max_cast_edit = QLineEdit()
        self.spells_table.table.setCellWidget(index, 8, max_cast_edit)
        if spell:
            max_cast_edit.setText(str(spell.max_cast))

        min_range_edit = QLineEdit()
        self.spells_table.table.setCellWidget(index, 9, min_range_edit)
        if spell:
            min_range_edit.setText(str(spell.min_range))

        range_edit = QLineEdit()
        self.spells_table.table.setCellWidget(index, 10, range_edit)
        if spell:
            range_edit.setText(str(spell.range))

        duration_boost_edit = QLineEdit()
        self.spells_table.table.setCellWidget(index, 11, duration_boost_edit)
        if spell:
            duration_boost_edit.setText(str(spell.duration_boost))

        boostable_range_checkbox = QCheckBox()
        self.spells_table.table.setCellWidget(index, 12, boostable_range_checkbox)
        if spell:
            boostable_range_checkbox.setChecked(spell.boostable_range)

        level_edit = QLineEdit()
        self.spells_table.table.setCellWidget(index, 13, level_edit)
        if spell:
            level_edit.setText(str(spell.level))

        delete_btn = PushButtonIcon("delete.svg")
        delete_btn.setCheckable(False)
        self.spells_table.table.setCellWidget(index, 14, delete_btn)
        delete_btn.clicked.connect(partial(self.on_delete_spell, index))

        self.spell_edits[index] = SpellInfoEdits(
            name_edit=name_edit,
            index_edit=index_edit,
            disenchantment_checkbox=disenchantment_checkbox,
            elem_combo=elem_combo,
            ap_cost_edit=ap_cost_edit,
            boost_combo=boost_combo,
            boostable_range_checkbox=boostable_range_checkbox,
            duration_boost_edit=duration_boost_edit,
            for_enemy_checkbox=for_enemy_checkbox,
            healing_checkbox=healing_checkbox,
            level_edit=level_edit,
            max_cast_edit=max_cast_edit,
            min_range_edit=min_range_edit,
            range_edit=range_edit,
        )

    def update_delete_buttons(self):
        for row_index in range(self.spells_table.table.rowCount()):
            delete_btn = self.spells_table.table.cellWidget(row_index, 14)
            assert isinstance(delete_btn, PushButtonIcon)
            if delete_btn is not None:
                delete_btn.clicked.disconnect()
                delete_btn.clicked.connect(partial(self.on_delete_spell, row_index))

    def on_delete_spell(self, index: int):
        if index in self.spell_edits:
            del self.spell_edits[index]
        self.spells_table.table.removeRow(index)
        self.update_delete_buttons()

from dataclasses import dataclass, field
from logging import Logger

import numpy

from D2Shared.shared.consts.adaptative.positions import (
    CLEAR_SEARCH_INVENTORY_POSITION,
    FIRST_OBJECT_INVENTORY_POSITION,
    LINES_COLUMNS_POSITION,
    MERGE_POSITION,
    RESOURCES_INVENTORY_POSITION,
    SEARCH_INVENTORY_POSITION,
)
from D2Shared.shared.schemas.equipment import ReadEquipmentSchema
from D2Shared.shared.schemas.stat import BaseLineSchema, StatSchema
from src.bots.dofus.elements.smithmagic_workshop import SmithMagicWorkshop
from src.bots.modules.fm.fm_analyser import FmAnalyser
from src.gui.signals.bot_signals import BotSignals
from src.services.equipment import EquipmentService
from src.services.line import LineService
from src.services.session import ServiceSession
from src.utils.time import wait
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller


@dataclass
class Fm:
    bot_signals: BotSignals
    controller: Controller
    service: ServiceSession
    fm_analyser: FmAnalyser
    logger: Logger
    smithmagic_workshop: SmithMagicWorkshop
    capturer: Capturer
    _searched_rune_name: str | None = field(default=None, init=False)

    def run(
        self,
        target_lines: list[BaseLineSchema],
        exo_stat: StatSchema | None = None,
        equipment: ReadEquipmentSchema | None = None,
    ):
        self._searched_rune_name = None
        old_img: numpy.ndarray | None = None
        while True:
            wait((0.3, 3), is_weighted=True, coeff=3)
            img = self.capturer.capture()
            if not self.smithmagic_workshop.has_history_changed(old_img, img):
                continue
            current_lines: list[BaseLineSchema] | None = (
                self.fm_analyser.get_stats_item_selected(img)
            )
            if current_lines is None:
                self.logger.info("Could not get stats of item")
                return None
            self.logger.info(f"Current lines : {current_lines}")
            if self.put_rune(current_lines, target_lines, exo_stat, equipment) is True:
                self.logger.info("Target item achieved")
                return None
            old_img = img

    def search_rune(self, name: str) -> None:
        self.controller.click(RESOURCES_INVENTORY_POSITION)
        self.controller.click(CLEAR_SEARCH_INVENTORY_POSITION)
        self.controller.send_text(name, pos=SEARCH_INVENTORY_POSITION)
        wait()
        self._searched_rune_name = name

    def merge_rune_by_name(self, name: str) -> None:
        if self._searched_rune_name != name:
            self.search_rune(name)
        self.controller.click(FIRST_OBJECT_INVENTORY_POSITION, count=2)
        wait((0.6, 1.5))
        self.controller.click(MERGE_POSITION)

    def put_exo(
        self,
        current_item_lines: list[BaseLineSchema],
        exo_stat: StatSchema,
    ) -> bool:
        related_curr_line = next(
            (_line for _line in current_item_lines if _line.stat.id == exo_stat.id),
            None,
        )
        if related_curr_line is not None:
            # found exo stat in current lines, success
            return True
        self.merge_rune_by_name(exo_stat.runes[0].name)

        return False

    def put_rune(
        self,
        current_item_lines: list[BaseLineSchema],
        target_item_lines: list[BaseLineSchema],
        exo_stat: StatSchema | None = None,
        equipment: ReadEquipmentSchema | None = None,
    ) -> bool:
        line_prio = self.fm_analyser.get_highest_priority_line(
            current_item_lines, target_item_lines
        )
        if line_prio is None:
            self.logger.info("Target lines achieved")
            if equipment:
                equipment.count_lines_achieved += 1
                EquipmentService.increment_count_achieved(self.service, equipment.id)
                self.bot_signals.fm_new_equipment_datas.emit(equipment)
            if exo_stat:
                return self.put_exo(current_item_lines, exo_stat)
            return True

        col_rune_info = self.fm_analyser.get_optimal_index_rune_for_target_line(
            line_prio.current_line, line_prio.target_line
        )
        if col_rune_info is None:
            raise ValueError(
                f"{line_prio.current_line.value} -> {line_prio.target_line.value} for {line_prio.current_line.stat.name}"
            )
        col_index, rune = col_rune_info
        self.controller.click(LINES_COLUMNS_POSITION[line_prio.index][col_index])

        self.logger.info(f"clicked line {line_prio.index} column {col_index}")

        if equipment:
            related_target_line = next(
                _elem
                for _elem in equipment.lines
                if _elem.stat_id == line_prio.target_line.stat_id
            )
            related_target_line.spent_quantity += rune.stat_quantity
            LineService.add_spent_quantity(
                self.service, related_target_line.id, rune.stat_quantity
            )
            self.bot_signals.fm_new_equipment_datas.emit(equipment)

        return False

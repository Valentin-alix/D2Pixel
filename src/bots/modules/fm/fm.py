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
from src.common.randomizer import wait
from src.gui.signals.bot_signals import BotSignals
from src.services.equipment import EquipmentService
from src.services.line import LineService
from src.services.session import ServiceSession
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller


class Fm:
    def __init__(
        self,
        bot_signals: BotSignals,
        controller: Controller,
        service: ServiceSession,
        fm_analyser: FmAnalyser,
        logger: Logger,
        smithmagic_workshop: SmithMagicWorkshop,
        capturer: Capturer,
    ) -> None:
        self.bot_signals = bot_signals
        self.controller = controller
        self.service = service
        self.fm_analyser = fm_analyser
        self.logger = logger
        self.smithmagic_workshop = smithmagic_workshop
        self.capturer = capturer

    def run(
        self,
        target_lines: list[BaseLineSchema],
        exo_stat: StatSchema | None = None,
        equipment: ReadEquipmentSchema | None = None,
    ):
        old_img: numpy.ndarray | None = None
        while True:
            wait((0.3, 0.5))
            img = self.capturer.capture()
            if not self.smithmagic_workshop.has_history_changed(old_img, img):
                continue
            current_lines: list[BaseLineSchema] | None = (
                self.fm_analyser.get_stats_item_selected(img)
            )
            self.logger.info(f"Current lines : {current_lines}")
            if current_lines is None:
                self.logger.info("Could not get stats of item")
                return None
            if self.put_rune(current_lines, target_lines, exo_stat, equipment) is True:
                self.logger.info("Target item achieved")
                return None
            old_img = img

    def place_rune_by_name(self, name: str):
        self.controller.click(RESOURCES_INVENTORY_POSITION)
        self.controller.click(CLEAR_SEARCH_INVENTORY_POSITION)
        self.controller.send_text(name, pos=SEARCH_INVENTORY_POSITION)
        wait()
        self.controller.click(FIRST_OBJECT_INVENTORY_POSITION, count=2)

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
        self.place_rune_by_name(exo_stat.runes[0].name)
        wait((0.6, 1))
        self.controller.click(MERGE_POSITION)
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
                self.bot_signals.fm_new_count_achieved.emit(
                    equipment.count_lines_achieved
                )
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
            self.bot_signals.fm_new_line_value.emit(
                (related_target_line.spent_quantity, related_target_line.stat_id)
            )

        return False

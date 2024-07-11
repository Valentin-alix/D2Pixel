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
from D2Shared.shared.schemas.stat import LineSchema, StatSchema
from src.bots.dofus.elements.smithmagic_workshop import SmithMagicWorkshop
from src.bots.modules.fm.fm_analyser import FmAnalyser
from src.common.randomizer import wait
from src.services.session import ServiceSession
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller


class Fm:
    def __init__(
        self,
        controller: Controller,
        service: ServiceSession,
        fm_analyser: FmAnalyser,
        logger: Logger,
        smithmagic_workshop: SmithMagicWorkshop,
        capturer: Capturer,
    ) -> None:
        self.controller = controller
        self.service = service
        self.fm_analyser = fm_analyser
        self.logger = logger
        self.smithmagic_workshop = smithmagic_workshop
        self.capturer = capturer

    def run(self, target_lines: list[LineSchema], exo: StatSchema | None = None):
        old_img: numpy.ndarray | None = None
        while True:
            wait((0.3, 1))
            img = self.capturer.capture()
            if not self.smithmagic_workshop.has_history_changed(old_img, img):
                continue
            current_lines = self.fm_analyser.get_stats_item_selected(img)
            if current_lines is None:
                self.logger.info("Could not get stats of item")
                return None
            if self.put_rune(current_lines, target_lines, exo) is True:
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
        current_item_lines: list[LineSchema],
        exo_stat: StatSchema | None = None,
    ) -> bool:
        if exo_stat is None:
            return True
        if (
            next(
                (
                    line
                    for line in current_item_lines
                    if line.stat.name == exo_stat.name
                ),
                None,
            )
            is not None
        ):
            return True
        self.place_rune_by_name(exo_stat.runes[0].name)
        wait((0.6, 1))
        self.controller.click(MERGE_POSITION)
        return False

    def put_rune(
        self,
        current_item_lines: list[LineSchema],
        target_item_lines: list[LineSchema],
        exo_stat: StatSchema | None = None,
    ) -> bool:
        line = self.fm_analyser.get_highest_priority_line(
            current_item_lines, target_item_lines
        )
        if line is None:
            return self.put_exo(current_item_lines, exo_stat)

        column = self.fm_analyser.get_optimal_index_rune_for_target_line(
            line.current_line, line.target_line
        )
        if column is None:
            raise ValueError(
                f"{line.current_line.value} -> {line.target_line.value} for {line.current_line.stat.name}"
            )

        self.controller.click(LINES_COLUMNS_POSITION[line.index][column])

        self.logger.info(f"clicked line {line.index} column {column}")

        return False
from logging import Logger
import numpy
import tesserocr


from D2Shared.shared.consts.adaptative.positions import (
    FIRST_OBJECT_INVENTORY_POSITION,
    LINES_COLUMNS_POSITION,
    MERGE_POSITION,
    RESOURCES_INVENTORY_POSITION,
    SEARCH_INVENTORY_POSITION,
)
from D2Shared.shared.consts.adaptative.regions import MERGE_AREA
from D2Shared.shared.schemas.stat import LineSchema
from src.bots.dofus.elements.smithmagic_workshop import SmithMagicWorkshop
from src.bots.modules.fm.fm_line_analyser import FmLineAnalyser
from src.common.randomizer import wait
from src.exceptions import UnknowStateException
from src.image_manager.ocr import BASE_CONFIG
from src.services.session import ServiceSession
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller


class Fm:
    def __init__(
        self,
        controller: Controller,
        service: ServiceSession,
        fm_line_analyser: FmLineAnalyser,
        logger: Logger,
        smithmagic_workshop: SmithMagicWorkshop,
        capturer: Capturer,
    ) -> None:
        self.controller = controller
        self.service = service
        self.fm_line_analyser = fm_line_analyser
        self.logger = logger
        self.smithmagic_workshop = smithmagic_workshop
        self.capturer = capturer

    def run(self, target_lines: list[LineSchema], exo: LineSchema | None = None):
        old_img: numpy.ndarray | None = None
        while True:
            wait((1, 1.5))
            img = self.capturer.capture()
            if not self.smithmagic_workshop.has_history_changed(old_img, img):
                continue
            with tesserocr.PyTessBaseAPI(**BASE_CONFIG) as tes_api:
                current_lines = self.get_stats_item_selected(img, tes_api)
                if current_lines is None:
                    self.logger.info("Could not get stats of item")
                    return None
                if self.put_rune(current_lines, target_lines, exo) is True:
                    self.logger.info("Target item achieved")
                    return None
                old_img = img

    def place_rune_by_name(self, name: str):
        self.controller.click(RESOURCES_INVENTORY_POSITION)
        self.controller.send_text(name, pos=SEARCH_INVENTORY_POSITION)
        self.controller.click(FIRST_OBJECT_INVENTORY_POSITION, count=2)

    def put_exo(
        self,
        current_item_lines: list[LineSchema],
        exo_line: LineSchema | None = None,
    ) -> bool:
        if exo_line is None:
            return True
        if (
            next(
                (
                    line
                    for line in current_item_lines
                    if line.stat.name == exo_line.stat.name
                ),
                None,
            )
            is not None
        ):
            return True
        self.place_rune_by_name(exo_line.stat.runes[0].name)
        wait((1, 1.5))
        self.controller.click(MERGE_POSITION)
        return False

    def put_rune(
        self,
        current_item_lines: list[LineSchema],
        target_item_lines: list[LineSchema],
        exo_line: LineSchema | None = None,
    ) -> bool:
        line = self.fm_line_analyser.get_highest_priority_line(
            current_item_lines, target_item_lines
        )
        if line is None:
            return self.put_exo(current_item_lines, exo_line)

        column = self.fm_line_analyser.get_optimal_index_rune_for_target_line(
            line.current_line, line.target_line
        )
        if column is None:
            raise ValueError(
                f"{line.current_line.value} -> {line.target_line.value} for {line.current_line.stat.name}"
            )

        self.controller.click(LINES_COLUMNS_POSITION[line.index][column])

        self.logger.info(f"clicked line {line.index} column {column}")

        return False

    def is_on_smithmagic_workshop(
        self, image: numpy.ndarray, tes_api: tesserocr.PyTessBaseAPI
    ) -> bool:
        tes_api.SetImage(image)
        tes_api.SetRectangle(
            MERGE_AREA.left,
            MERGE_AREA.top,
            MERGE_AREA.right - MERGE_AREA.left,
            MERGE_AREA.bot - MERGE_AREA.top,
        )
        text = self.fm_line_analyser.clean_line_text(tes_api.GetUTF8Text())
        return text == "fusionner"

    def get_stats_item_selected(
        self, img: numpy.ndarray, tes_api: tesserocr.PyTessBaseAPI
    ) -> list[LineSchema] | None:
        if self.is_on_smithmagic_workshop(img, tes_api):
            try:
                parsed_item = self.fm_line_analyser.get_lines_from_img(img, tes_api)
                return parsed_item
            except ValueError:
                raise UnknowStateException(img, "magic_stat_item_parse_err")
        return None

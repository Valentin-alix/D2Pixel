import re
from dataclasses import dataclass
from logging import Logger

import numpy
import tesserocr

from D2Shared.shared.consts.adaptative.regions import LINE_AREAS, LINE_MAX_AREAS
from D2Shared.shared.schemas.stat import (
    BaseLineSchema,
    RuneSchema,
    StatSchema,
)
from D2Shared.shared.utils.clean import clean_line_text
from D2Shared.shared.utils.randomizer import multiply_offset
from D2Shared.shared.utils.text_similarity import get_similarity
from src.bots.dofus.elements.smithmagic_workshop import SmithMagicWorkshop
from src.exceptions import UnknowStateException
from src.image_manager.ocr import (
    BASE_CONFIG,
    get_text_from_image,
    set_config_for_ocr_number,
)
from src.image_manager.transformation import (
    crop_image,
    img_to_gray,
)
from src.services.session import ServiceSession
from src.services.stat import StatService


@dataclass
class LinePriority:
    index: int
    current_line: BaseLineSchema
    target_line: BaseLineSchema


@dataclass
class FmAnalyser:
    logger: Logger
    service: ServiceSession
    smithmagic_workshop: SmithMagicWorkshop

    def get_optimal_index_rune_for_target_line(
        self,
        current_line: BaseLineSchema,
        target_line: BaseLineSchema,
    ) -> tuple[int, RuneSchema] | None:
        ordered_runes: list[RuneSchema] = sorted(
            current_line.stat.runes, key=lambda rune: rune.stat_quantity, reverse=True
        )
        for index, rune in enumerate(ordered_runes):
            if (
                current_line.value + rune.stat_quantity <= target_line.value
                or index == len(ordered_runes) - 1
                or current_line.value >= 20 * ordered_runes[index + 1].stat_quantity
            ):
                # si le resultat donne une valeur inférieur ou égale à la cible
                # ou si la valeur recherché est trop haute pour la rune suivante
                related_index: int = len(ordered_runes) - 1 - index
                return related_index, rune

        return None

    def get_highest_priority_line(
        self, current_lines: list[BaseLineSchema], target_lines: list[BaseLineSchema]
    ) -> LinePriority | None:
        priority_line_with_weight: tuple[LinePriority, float] | None = None

        for target_line in target_lines:
            if target_line.value <= 0:
                # ignore negative values
                continue
            try:
                index, current_line = next(
                    (index, _line)
                    for index, _line in enumerate(current_lines)
                    if target_line.stat.name == _line.stat.name
                )
            except StopIteration:
                self.logger.error(f"Did not found {target_line.stat.name}")
                raise

            difference_weight: float = current_line.value / target_line.value
            if difference_weight >= 1.0:
                # ignore achieved lines
                continue
            difference_weight *= multiply_offset((0.95, 1))

            # TODO check also the remainder
            # if target_line.stat.name in BIG_STATS_NAMES:
            #     difference_weight = 1  # put big stats at last

            if priority_line_with_weight is None or (
                priority_line_with_weight[1] > difference_weight
            ):
                priority_line_with_weight = (
                    LinePriority(
                        current_line=current_line, target_line=target_line, index=index
                    ),
                    difference_weight,
                )
        return priority_line_with_weight[0] if priority_line_with_weight else None

    def _get_line_from_text(self, line_text: str) -> BaseLineSchema | None:
        def extract_value_from_text(text: str) -> int:
            value_str: str = "".join(re.findall(r"\d", text))
            if len(value_str) > 0:
                value: int = int(value_str)
                if text.startswith("-"):
                    value = -value
            else:
                value: int = 0
            return value

        def extract_name_from_text(text: str) -> str:
            return "".join(
                (char for char in text if not char.isdigit() and char != "-")
            )

        cleaned_text: str = clean_line_text(line_text)
        if len(cleaned_text) > 0:
            value: int = extract_value_from_text(cleaned_text)
            name: str = extract_name_from_text(cleaned_text)

            stats = StatService.get_stats(self.service)
            most_similar_stat: tuple[StatSchema, float] | None = max(
                [
                    (stat, sim_words)
                    for stat in stats
                    if (sim_words := get_similarity(clean_line_text(stat.name), name))
                    > 0.8
                ],
                key=lambda _elem: _elem[1],
                default=None,
            )
            if most_similar_stat is None:
                raise ValueError(f"cleaned_text: {cleaned_text} give no stat known")
            stat, _ = most_similar_stat
            line: BaseLineSchema = BaseLineSchema(
                value=value, stat_id=stat.id, stat=stat
            )
            return line
        return None

    def get_current_lines_from_img(self, image: numpy.ndarray) -> list[BaseLineSchema]:
        try:
            lines: list[BaseLineSchema] = []
            with tesserocr.PyTessBaseAPI(**BASE_CONFIG) as tes_api:
                for line_area in LINE_AREAS:
                    croped_img = crop_image(image, line_area)
                    croped_img = img_to_gray(croped_img)
                    text = get_text_from_image(croped_img, tes_api)
                    line_text = self._get_line_from_text(text)
                    if line_text is not None:
                        lines.append(line_text)
        except ValueError:
            raise UnknowStateException(image, "magic_stat_item_parse_err")
        return lines

    def get_max_lines_values_from_img(self, image: numpy.ndarray) -> list[int]:
        try:
            max_lines_values: list[int] = []
            with tesserocr.PyTessBaseAPI(**BASE_CONFIG) as tes_api:
                set_config_for_ocr_number(tes_api, white_list="-0123456789")
                for line_area in LINE_MAX_AREAS:
                    croped_img = crop_image(image, line_area)
                    text = get_text_from_image(croped_img, tes_api)
                    if text == "":
                        break
                    max_lines_values.append(int(text))
            self.logger.info(max_lines_values)
        except ValueError:
            raise UnknowStateException(image, "magic_stat_item_parse_max_err")
        return max_lines_values

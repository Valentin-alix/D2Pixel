import re
import numpy
import tesserocr
from pydantic import BaseModel
from PIL import Image as Img
from D2Shared.shared.consts.adaptative.regions import LINE_AREAS
from D2Shared.shared.schemas.stat import LineSchema, StatSchema
from D2Shared.shared.utils.clean import clean_line_text
from D2Shared.shared.utils.text_similarity import get_similarity
from src.bots.dofus.elements.smithmagic_workshop import SmithMagicWorkshop
from src.exceptions import UnknowStateException
from src.image_manager.ocr import BASE_CONFIG
from src.services.session import ServiceSession
from src.services.stat import StatService


class LinePriority(BaseModel):
    index: int
    current_line: LineSchema
    target_line: LineSchema


class FmAnalyser:
    def __init__(
        self, service: ServiceSession, smithmagic_workshop: SmithMagicWorkshop
    ) -> None:
        self.service = service
        self.smithmagic_workshop = smithmagic_workshop

    def get_stats_item_selected(self, img: numpy.ndarray) -> list[LineSchema] | None:
        if self.smithmagic_workshop.is_on_smithmagic_workshop(img):
            try:
                parsed_item = self.get_lines_from_img(img)
                return parsed_item
            except ValueError:
                raise UnknowStateException(img, "magic_stat_item_parse_err")
        return None

    def get_line_from_text(self, line_text: str) -> LineSchema | None:
        def extract_value_from_text(text: str) -> int:
            value = "".join(re.findall(r"\d", text))
            if len(value) > 0:
                value = int(value)
                if text.startswith("-"):
                    value = -value
            else:
                value = 0
            return value

        def extract_name_from_text(text: str) -> str:
            return "".join(
                (char for char in text if not char.isdigit() and char != "-")
            )

        cleaned_text = clean_line_text(line_text)
        if len(cleaned_text) > 0:
            value = extract_value_from_text(cleaned_text)
            name = extract_name_from_text(cleaned_text)

            stats = StatService.get_stats(self.service)
            most_similar_stat: tuple[StatSchema, float] | None = max(
                [
                    (stat, sim_words)
                    for stat in stats
                    if (sim_words := get_similarity(clean_line_text(stat.name), name))
                    > 0.8
                ],
                key=lambda elem: elem[1],
                default=None,
            )
            if most_similar_stat is None:
                raise ValueError(f"cleaned_text: {cleaned_text} give no stat known")
            stat, _ = most_similar_stat
            line = LineSchema(value=value, stat_id=stat.id, stat=stat)
            return line
        return None

    def get_lines_from_img(self, image: numpy.ndarray) -> list[LineSchema]:
        lines: list[LineSchema] = []
        pil_img = Img.fromarray(image)
        with tesserocr.PyTessBaseAPI(**BASE_CONFIG) as tes_api:
            tes_api.SetImage(pil_img)
            for line_area in LINE_AREAS:
                tes_api.SetRectangle(
                    line_area.left,
                    line_area.top,
                    line_area.right - line_area.left,
                    line_area.bot - line_area.top,
                )
                text = tes_api.GetUTF8Text()
                line_text = self.get_line_from_text(text)
                if line_text is not None:
                    lines.append(line_text)
        return lines

    def get_optimal_index_rune_for_target_line(
        self, current_line: LineSchema, target_line: LineSchema
    ) -> int | None:
        for index, rune in list(enumerate(current_line.stat.runes))[::-1]:
            if (
                target_line.value - current_line.value
            ) >= rune.stat_quantity or current_line.value / rune.stat_quantity >= 5:
                return index

        return None

    def get_highest_priority_line(
        self, current_lines: list[LineSchema], target_lines: list[LineSchema]
    ) -> LinePriority | None:
        priority_line_weight: tuple[LinePriority, float] | None = None

        for target_line in target_lines:
            if target_line.value <= 0:
                continue
            index, current_line = next(
                (index, _line)
                for index, _line in enumerate(current_lines)
                if target_line.stat.name == _line.stat.name
            )
            difference_weight = current_line.value / target_line.value
            if difference_weight >= 1.0:
                continue
            if (
                priority_line_weight is None
                or priority_line_weight[1] > difference_weight
            ):
                priority_line_weight = (
                    LinePriority(
                        current_line=current_line, target_line=target_line, index=index
                    ),
                    difference_weight,
                )
        return priority_line_weight[0] if priority_line_weight else None

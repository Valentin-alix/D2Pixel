import numpy
import unidecode
from EzreD2Shared.shared.consts.adaptative.consts import (
    INFO_JOB_IMPOSSIBLE_OFFSET_BOT,
    INFO_JOB_IMPOSSIBLE_OFFSET_RIGHT,
    INFO_JOB_LVLUP_OFFSET_BOT,
    INFO_JOB_LVLUP_OFFSET_RIGHT,
)
from EzreD2Shared.shared.schemas.job import JobSchema
from EzreD2Shared.shared.schemas.region import RegionSchema
from EzreD2Shared.shared.utils.text_similarity import get_similarity

from src.bots.dofus.hud.info_popup.info_popup import clean_info_popup_img
from src.exceptions import UnknowStateException
from src.image_manager.ocr import get_text_from_image
from src.services.job import JobService


def parse_job_level_info_impossible(text: str) -> tuple[JobSchema, int] | None:
    res = text.split("\n")
    job_text = unidecode.unidecode(res[0].split(" ")[0], "utf-8")

    job = JobService.find_job_by_text(job_text)
    if job is None:
        return None

    actual_lvl = int(res[1].split(" ")[2])
    return job, actual_lvl


def parse_job_new_level(text: str) -> tuple[JobSchema, int]:
    print(text)

    text = text.replace(",", ".")
    first_line = text.split(".")[0]
    job_info = unidecode.unidecode(
        first_line.replace("[", "")
        .replace("]", "")
        .replace(".", "")
        .replace("\n", " "),
        "utf-8",
    ).split(" ")
    print(job_info)

    level_index, _ = max(
        [
            (index + 1, get_similarity(word, "niveau"))
            for index, word in enumerate(job_info)
        ],
        key=lambda elem: elem[1],
    )

    job = JobService.find_job_by_text(job_info[2])
    if job is None:
        raise ValueError(f"job cannot be None, from text : {text}")

    level_index = int(job_info[level_index])

    return job, level_index


def get_job_level_from_level_up(
    img: numpy.ndarray, area: RegionSchema
) -> tuple[JobSchema, int]:
    def get_area_info_from_level_up(region_level_up: RegionSchema) -> RegionSchema:
        return RegionSchema(
            left=region_level_up.left,
            right=region_level_up.right + INFO_JOB_LVLUP_OFFSET_RIGHT,
            top=region_level_up.bot,
            bot=region_level_up.bot + INFO_JOB_LVLUP_OFFSET_BOT,
        )

    def clean_info_modal_level_up_img(
        img: numpy.ndarray, area: RegionSchema
    ) -> numpy.ndarray:
        img = clean_info_popup_img(img, area)
        return img

    def get_info_modal_level_up_job(img: numpy.ndarray, area: RegionSchema) -> str:
        img = clean_info_modal_level_up_img(img, area)
        text = get_text_from_image(img)
        return text

    try:
        job_lvl_area = get_area_info_from_level_up(area)
        job_text = get_info_modal_level_up_job(img, job_lvl_area)
        job, level = parse_job_new_level(job_text)
        return job, level
    except ValueError:
        raise UnknowStateException(img, "job_lvl_up_parse")


def get_job_level_from_impossible_recolt(
    img: numpy.ndarray, area: RegionSchema
) -> tuple[JobSchema, int] | None:
    def get_area_info_from_impossible_recolt(
        region_impossible_recolt: RegionSchema,
    ) -> RegionSchema:
        return RegionSchema(
            left=region_impossible_recolt.left,
            right=region_impossible_recolt.right + INFO_JOB_IMPOSSIBLE_OFFSET_RIGHT,
            top=region_impossible_recolt.bot,
            bot=region_impossible_recolt.bot + INFO_JOB_IMPOSSIBLE_OFFSET_BOT,
        )

    def get_info_modal_impossible_recolt(img: numpy.ndarray, area: RegionSchema) -> str:
        img = clean_info_popup_img(img, area)
        text = get_text_from_image(img)
        return text

    job_lvl_area = get_area_info_from_impossible_recolt(area)
    job_text = get_info_modal_impossible_recolt(img, job_lvl_area)
    job_info = parse_job_level_info_impossible(job_text)
    if job_info is None:
        return None
    return job_info

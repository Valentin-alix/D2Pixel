from dataclasses import dataclass, field
from logging import Logger
from time import sleep

import numpy
import tesserocr

from D2Shared.shared.consts.adaptative.consts import MODAL_LVLUP_OFFSET_RIGHT
from D2Shared.shared.consts.object_configs import ObjectConfigs
from D2Shared.shared.entities.object_search_config import ObjectSearchConfig
from D2Shared.shared.entities.position import Position
from D2Shared.shared.schemas.character import UpdateCharacterSchema
from D2Shared.shared.schemas.region import RegionSchema
from src.bots.dofus.hud.info_popup.info_popup import EventInfoPopup
from src.bots.dofus.hud.info_popup.job_level import JobParser
from src.exceptions import UnknowStateException
from src.image_manager.ocr import (
    BASE_CONFIG,
    get_text_from_image,
    set_config_for_ocr_number,
)
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.image_manager.transformation import crop_image
from src.services.character import CharacterService
from src.services.session import ServiceSession
from src.states.character_state import CharacterState
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller


@dataclass
class Hud:
    logger: Logger

    close_interface_configs: list[ObjectSearchConfig] = field(
        default_factory=lambda: [
            ObjectConfigs.Cross.grey_on_black,
            ObjectConfigs.Cross.black_on_grey,
            ObjectConfigs.Cross.small_black_on_grey,
            ObjectConfigs.Cross.map,
            ObjectConfigs.Button.ok,
            ObjectConfigs.Button.yes,
        ],
        init=False,
    )

    def get_level_up_number(
        self, img: numpy.ndarray, level_up_text_position: Position, region: RegionSchema
    ) -> int:
        height, width = region.bot - region.top, region.right - region.left
        level_up_number_area = RegionSchema(
            left=level_up_text_position.x_pos + width // 2,
            right=level_up_text_position.x_pos + width + MODAL_LVLUP_OFFSET_RIGHT,
            top=level_up_text_position.y_pos - height // 2,
            bot=level_up_text_position.y_pos + height // 2,
        )
        cropped_img = crop_image(img, level_up_number_area)
        with tesserocr.PyTessBaseAPI(**BASE_CONFIG) as tes_api:
            set_config_for_ocr_number(tes_api)
            try:
                return int(get_text_from_image(cropped_img, tes_api))
            except ValueError:
                raise UnknowStateException(img, "lvl_up_number")


@dataclass
class HudSystem:
    hud: Hud
    image_manager: ImageManager
    character_state: CharacterState
    service: ServiceSession
    controller: Controller
    object_searcher: ObjectSearcher
    capturer: Capturer
    logger: Logger
    job_parser: JobParser

    def handle_level_up(
        self, img: numpy.ndarray, pos: Position, region: RegionSchema
    ) -> numpy.ndarray:
        new_level = self.hud.get_level_up_number(img, pos, region)

        character = self.character_state.character
        character.lvl = new_level
        character = CharacterService.update_character(
            self.service,
            UpdateCharacterSchema(
                id=character.id,
                lvl=character.lvl,
                po_bonus=character.po_bonus,
                elem=character.elem,
                server_id=character.server_id,
            ),
        )

        modal_ok_info = self.object_searcher.get_position(
            img, ObjectConfigs.Button.ok, force=True
        )
        self.controller.click(modal_ok_info[0])
        return self.image_manager.capturer.capture()

    def handle_info_modal(
        self, img: numpy.ndarray
    ) -> tuple[numpy.ndarray, set[EventInfoPopup]]:
        events_info_modal: set[EventInfoPopup] = set()

        if (
            quit_info := self.image_manager.object_searcher.get_position(
                img, ObjectConfigs.Cross.green_info_modal
            )
        ) is None:
            return img, events_info_modal

        self.logger.info("Found modal info")
        if imp_recolt_info := self.image_manager.object_searcher.get_position(
            img, ObjectConfigs.Harvest.impossible_recolt_text
        ):
            job_info = self.job_parser.get_job_level_from_impossible_recolt(
                img, imp_recolt_info[1].region
            )
            if job_info:
                job, level = job_info
                related_job_info = next(
                    (
                        elem
                        for elem in self.character_state.character.jobs_infos
                        if elem.job_id == job.id
                    )
                )
                related_job_info.lvl = level
                CharacterService.update_job_infos(
                    self.service,
                    self.character_state.character.id,
                    self.character_state.character.jobs_infos,
                )
                self.logger.info(f"new character job lvl : {job}:{level}")
                if (level % 10) == 0:
                    events_info_modal.add(EventInfoPopup.LVL_UP_JOB)
        elif lvl_up_info := self.object_searcher.get_position(
            img, ObjectConfigs.Job.level_up
        ):
            job, level = self.job_parser.get_job_level_from_level_up(
                img, lvl_up_info[1].region
            )
            related_job_info = next(
                (
                    elem
                    for elem in self.character_state.character.jobs_infos
                    if elem.job_id == job.id
                )
            )
            related_job_info.lvl = level
            CharacterService.update_job_infos(
                self.service,
                self.character_state.character.id,
                self.character_state.character.jobs_infos,
            )
            if (level % 10) == 0:
                events_info_modal.add(EventInfoPopup.LVL_UP_JOB)

        self.controller.click(quit_info[0])
        img = self.capturer.capture()
        return img, events_info_modal

    def close_modal(
        self,
        ordered_configs: list[ObjectSearchConfig],
        img: numpy.ndarray,
        from_cache: bool = True,
    ) -> tuple[bool, numpy.ndarray]:
        """close modal by configs provided, return True if no modal found"""
        for config in ordered_configs:
            pos_info = self.object_searcher.get_position(
                img, config, use_cache=from_cache
            )
            if pos_info is None:
                continue
            pos, template_found_place = pos_info
            self.controller.click(pos)
            sleep(0.3)
            img = self.capturer.capture()
            if (
                next(
                    self.object_searcher.iter_position_from_template_info(
                        img, config, [template_found_place]
                    ),
                    None,
                )
                is None
            ):
                self.logger.info(f"Closed modal with {config.id}")
                return False, img
        return True, img

    def close_modals(
        self,
        img: numpy.ndarray,
        ordered_configs_to_check: list[ObjectSearchConfig] = [
            ObjectConfigs.Cross.black_on_grey,
            ObjectConfigs.Cross.small_black_on_grey,
        ],
        from_cache: bool = True,
    ) -> numpy.ndarray:
        MAX_ITERATION = 15
        for _ in range(MAX_ITERATION):
            no_cross, img = self.close_modal(ordered_configs_to_check, img, from_cache)
            if no_cross:
                return img
        raise UnknowStateException(img, "too_much_iteration_close_modal")

    def clean_interface(
        self, img: numpy.ndarray, from_cache: bool = False
    ) -> numpy.ndarray:
        return self.close_modals(
            img,
            ordered_configs_to_check=self.hud.close_interface_configs,
            from_cache=from_cache,
        )

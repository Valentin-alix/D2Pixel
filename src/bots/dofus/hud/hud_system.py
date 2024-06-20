from time import sleep

import numpy
import tesserocr
from EzreD2Shared.shared.consts.adaptative.consts import MODAL_LVLUP_OFFSET_RIGHT
from EzreD2Shared.shared.consts.object_configs import ObjectConfigs
from EzreD2Shared.shared.entities.object_search_config import ObjectSearchConfig
from EzreD2Shared.shared.entities.position import Position
from EzreD2Shared.shared.schemas.region import RegionSchema

from src.bots.dofus.dofus_bot import DofusBot
from src.bots.dofus.hud.info_popup.info_popup import EventInfoPopup
from src.bots.dofus.hud.info_popup.job_level import (
    get_job_level_from_impossible_recolt,
    get_job_level_from_level_up,
)
from src.exceptions import UnknowStateException
from src.image_manager.ocr import (
    BASE_CONFIG,
    get_text_from_image,
    set_config_for_ocr_number,
)
from src.image_manager.transformation import crop_image
from src.services.character import CharacterService


class Hud(DofusBot):
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


class HudSystem(Hud):
    def handle_level_up(
        self, img: numpy.ndarray, pos: Position, region: RegionSchema
    ) -> numpy.ndarray:
        new_level = self.get_level_up_number(img, pos, region)

        self.character.lvl = new_level
        self.character = CharacterService.update_character(self.character)

        modal_ok_info = self.get_position(img, ObjectConfigs.Button.ok, force=True)
        self.click(modal_ok_info[0])
        return self.capture()

    def handle_info_modal(
        self, img: numpy.ndarray
    ) -> tuple[numpy.ndarray, set[EventInfoPopup]]:
        events_info_modal: set[EventInfoPopup] = set()

        if (quit_info := self.get_position(img, ObjectConfigs.Cross.green)) is None:
            return img, events_info_modal

        self.log_info("Found modal info")
        if imp_recolt_info := self.get_position(
            img, ObjectConfigs.Harvest.impossible_recolt_text
        ):
            job_info = get_job_level_from_impossible_recolt(
                img, RegionSchema.model_validate(imp_recolt_info[1].region)
            )
            if job_info:
                job, level = job_info
                CharacterService.update_job_info(self.character.id, job.id, level)
                self.log_info(f"new character job lvl : {job}:{level}")
                if (level % 10) == 0:
                    events_info_modal.add(EventInfoPopup.LVL_UP_JOB)
        elif lvl_up_info := self.get_position(img, ObjectConfigs.Job.level_up):
            job, level = get_job_level_from_level_up(
                img,
                RegionSchema.model_validate(lvl_up_info[1].region),
            )
            CharacterService.update_job_info(self.character.id, job.id, level)
            if (level % 10) == 0:
                events_info_modal.add(EventInfoPopup.LVL_UP_JOB)

        self.click(quit_info[0])
        img = self.capture()
        return img, events_info_modal

    def close_modal(
        self, ordered_configs: list[ObjectSearchConfig], img: numpy.ndarray
    ) -> tuple[bool, numpy.ndarray]:
        """close modal by configs provided, return True if no modal found"""
        for config in ordered_configs:
            pos_info = self.get_position(img, config)
            if pos_info is None:
                continue
            pos, template_found_place = pos_info
            self.click(pos)
            sleep(0.3)
            img = self.capture()
            if (
                next(
                    self.iter_position_from_template_info(
                        img, config, [template_found_place]
                    ),
                    None,
                )
                is None
            ):
                self.log_info(f"Closed modal with {config.id}")
                return False, img
        return True, img

    def close_modals(
        self,
        img: numpy.ndarray,
        ordered_configs_to_check: list[ObjectSearchConfig] = [
            ObjectConfigs.Cross.bank_inventory_right,
            ObjectConfigs.Cross.info_win_fight,
        ],
    ) -> numpy.ndarray:
        MAX_ITERATION = 15
        for _ in range(MAX_ITERATION):
            no_cross, img = self.close_modal(ordered_configs_to_check, img)
            if no_cross:
                return img
        raise UnknowStateException(img, "too_much_iteration_close_modal")

    def clean_interface(self, img: numpy.ndarray) -> numpy.ndarray:
        return self.close_modals(
            img,
            ordered_configs_to_check=[
                ObjectConfigs.Cross.popup_info,
                ObjectConfigs.Cross.inverted,
                ObjectConfigs.Cross.map,
                ObjectConfigs.Cross.bank_inventory_right,
                ObjectConfigs.Cross.sale_hotel_inventory_right,
                ObjectConfigs.Cross.info_win_fight,
                ObjectConfigs.Cross.info_lose_fight,
                ObjectConfigs.Cross.connection_warning,
                ObjectConfigs.Button.ok,
                ObjectConfigs.Button.yes,
            ],
        )

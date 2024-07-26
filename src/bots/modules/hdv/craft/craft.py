from logging import Logger
from time import sleep

import win32con

from D2Shared.shared.consts.adaptative.positions import (
    COUNT_CRAFT_RECEIP_POSITION,
    DISPLAY_POSSIBLE_RECEIPE_POSITION,
    FIRST_SLOT_RECEIPE_POSITION,
    MERGE_CRAFT_POSITION,
    SEARCH_RECEIPE_POSITION,
)
from D2Shared.shared.consts.object_configs import ObjectConfigs
from D2Shared.shared.schemas.job import JobSchema
from D2Shared.shared.schemas.recipe import RecipeSchema
from src.bots.dofus.elements.bank import BankSystem
from src.bots.dofus.hud.hud_system import HudSystem
from src.bots.dofus.walker.buildings.workshop_building import WorkshopBuilding
from src.common.randomizer import wait
from src.entities.item import ItemProcessedStatus
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.character import CharacterService
from src.services.session import ServiceSession
from src.states.character_state import CharacterState
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller


class Crafter:
    def __init__(
        self,
        hud_sys: HudSystem,
        bank_sys: BankSystem,
        logger: Logger,
        image_manager: ImageManager,
        object_searcher: ObjectSearcher,
        capturer: Capturer,
        controller: Controller,
        workshop_building: WorkshopBuilding,
        service: ServiceSession,
        character_state: CharacterState,
    ) -> None:
        self.hud_sys = hud_sys
        self.bank_sys = bank_sys
        self.logger = logger
        self.object_searcher = object_searcher
        self.capturer = capturer
        self.image_manager = image_manager
        self.controller = controller
        self.workshop_building = workshop_building
        self.hud_sys = hud_sys
        self.service = service
        self.character_state = character_state

    def craft_from_inventory(self, recipes: set[RecipeSchema]) -> set[RecipeSchema]:
        """craft item in order of receipes given

        Args:
            recipes (set[Recipe]): ordered receipes
        Return:
            recipes_faileds (set[Recipe]): recipe that could not be crafted
        """
        recipes_faileds: set[RecipeSchema] = set()
        current_job: JobSchema | None = None
        for recipe in recipes:
            self.logger.info(f"Gonna craft {recipe}")
            if recipe.job != current_job:
                # go to workshop related
                if current_job is not None:
                    self.hud_sys.close_modals(
                        self.capturer.capture(),
                        ordered_configs_to_check=[
                            ObjectConfigs.Cross.bank_inventory_right
                        ],
                    )
                pos = self.workshop_building.go_workshop_for_job(recipe.job.name)
                self.logger.info(f"Go for {recipe.job.name}")
                self.workshop_building.open_material_workshop(pos)
                self.controller.click(DISPLAY_POSSIBLE_RECEIPE_POSITION)

            # search item in craft interface
            if recipe.job != current_job:
                self.controller.click(SEARCH_RECEIPE_POSITION)
                current_job = recipe.job
            else:
                self.controller.click(SEARCH_RECEIPE_POSITION, count=3)
                self.controller.key(win32con.VK_BACK)
            self.controller.send_text(recipe.result_item.name)
            sleep(1)
            if (
                self.object_searcher.get_position(
                    self.capturer.capture(), ObjectConfigs.Text.no_receipe
                )
                is None
            ):
                # item is craftable
                self.controller.click(FIRST_SLOT_RECEIPE_POSITION)
                wait()
                self.controller.click(COUNT_CRAFT_RECEIP_POSITION)
                self.controller.key(win32con.VK_RETURN)
                sleep(0.3)
                self.controller.click(MERGE_CRAFT_POSITION)
                wait((0.6, 1))
                CharacterService.add_bank_items(
                    self.service,
                    self.character_state.character.id,
                    [recipe.result_item_id],
                )
            else:
                self.logger.info(
                    f"Found no receipe possible in workshop for {recipe.result_item.name}"
                )
                recipes_faileds.add(recipe)

        img, _ = self.hud_sys.handle_info_modal(self.capturer.capture())
        if current_job is not None:
            self.hud_sys.close_modals(
                img,
                ordered_configs_to_check=[ObjectConfigs.Cross.bank_inventory_right],
            )

        return recipes_faileds

    def run_crafter(self, recipes: list[RecipeSchema]):
        """craft all input items based on coherent order (based on prerequire, level)

        Args:
            recipes (list[RecipeSchema]): list of recipes
        """
        self.bank_sys.bank_clear_inventory()

        recipes_inventory: set[RecipeSchema] = set()
        for recipe in recipes:
            while True:
                item_craft_status = self.bank_sys.bank_get_ingredients_item(recipe)
                if item_craft_status == ItemProcessedStatus.NOT_PROCESSED:
                    # go to next item
                    break
                recipes_inventory.add(recipe)
                if item_craft_status == ItemProcessedStatus.MAX_PROCESSED:
                    # go to next item
                    break
                # item is probably still craftable, go craft & stay on same item
                self.hud_sys.close_modals(
                    self.capturer.capture(),
                    ordered_configs_to_check=[ObjectConfigs.Cross.bank_inventory_right],
                )
                failed_recipes = self.craft_from_inventory(recipes_inventory)
                self.bank_sys.bank_clear_inventory()
                recipes_inventory.clear()
                if recipe in failed_recipes:
                    break

            CharacterService.remove_bank_items(
                self.service,
                self.character_state.character.id,
                [_elem.item_id for _elem in recipe.ingredients],
            )

        self.hud_sys.close_modals(
            self.capturer.capture(),
            ordered_configs_to_check=[ObjectConfigs.Cross.bank_inventory_right],
        )
        self.craft_from_inventory(recipes_inventory)

import win32con
from EzreD2Shared.shared.consts.adaptative.positions import (
    COUNT_CRAFT_RECEIP_POSITION,
    DISPLAY_POSSIBLE_RECEIPE_POSITION,
    FIRST_SLOT_RECEIPE_POSITION,
    MERGE_CRAFT_POSITION,
    SEARCH_RECEIPE_POSITION,
)
from EzreD2Shared.shared.consts.object_configs import ObjectConfigs
from EzreD2Shared.shared.schemas.job import JobSchema
from EzreD2Shared.shared.schemas.recipe import RecipeSchema
from EzreD2Shared.shared.utils.randomizer import wait

from src.bots.dofus.chat.chat_system import ChatSystem
from src.bots.dofus.elements.bank import BankSystem
from src.bots.dofus.walker.buildings.workshop_building import WorkshopBuilding
from src.entities.item import ItemProcessedStatus


class Crafter(WorkshopBuilding, BankSystem, ChatSystem):
    def craft_from_inventory(self, recipes: set[RecipeSchema]):
        """craft item in order of receipes given

        Args:
            receipes (list[Recipe]): ordered receipes
        """
        current_job: JobSchema | None = None
        for recipe in recipes:
            self.log_info(f"Gonna craft {recipe}")
            if recipe.job != current_job:
                # go to workshop related
                if current_job is not None:
                    self.close_modals(
                        self.capture(),
                        ordered_configs_to_check=[
                            ObjectConfigs.Cross.bank_inventory_right
                        ],
                    )
                pos = self.go_workshop_for_job(recipe.job.name)
                self.log_info(f"Go for {recipe.job.name}")
                self.open_material_workshop(pos)
                self.click(DISPLAY_POSSIBLE_RECEIPE_POSITION)

            # search item in craft interface
            if recipe.job != current_job:
                self.click(SEARCH_RECEIPE_POSITION)
                current_job = recipe.job
            else:
                self.click(SEARCH_RECEIPE_POSITION, count=3)
                self.key(win32con.VK_BACK)
            self.send_text(recipe.result_item.name)

            if self.get_position(self.capture(), ObjectConfigs.Text.no_receipe) is None:
                # item is craftable
                self.click(FIRST_SLOT_RECEIPE_POSITION)
                wait()
                self.click(COUNT_CRAFT_RECEIP_POSITION)
                self.key(win32con.VK_RETURN)
                self.click(MERGE_CRAFT_POSITION)
                wait()

        img, _ = self.handle_info_modal(self.capture())
        if current_job is not None:
            self.close_modals(
                img,
                ordered_configs_to_check=[ObjectConfigs.Cross.bank_inventory_right],
            )

    def run_crafter(self, recipes: list[RecipeSchema]):
        """craft all input items based on coherent order (based on prerequire, level)

        Args:
            items (list[ItemCraftInfo]): list of items (order doesn't matter)
        """
        self.bank_clear_inventory()

        recipes_inventory: set[RecipeSchema] = set()
        for recipe in recipes:
            while True:
                item_craft_status = self.bank_get_ingredients_item(recipe)
                if item_craft_status == ItemProcessedStatus.NOT_PROCESSED:
                    # go to next item
                    break
                recipes_inventory.add(recipe)
                if item_craft_status == ItemProcessedStatus.MAX_PROCESSED:
                    # go to next item
                    break
                # item is probably still craftable, go craft & stay on same item
                self.close_modals(
                    self.capture(),
                    ordered_configs_to_check=[ObjectConfigs.Cross.bank_inventory_right],
                )
                self.craft_from_inventory(recipes_inventory)
                self.bank_clear_inventory()
                recipes_inventory.clear()

        self.close_modals(
            self.capture(),
            ordered_configs_to_check=[ObjectConfigs.Cross.bank_inventory_right],
        )
        self.craft_from_inventory(recipes_inventory)

from time import sleep

import numpy
import win32con
from EzreD2Shared.shared.consts.adaptative.consts import (
    BANK_RECEIPE_SLOT_HEIGHT,
    BANK_RECEIPE_SLOT_INITIAL_Y,
    BANK_RECEIPE_TITLE_MAX_HEIGHT,
    BANK_RECEIPE_TITLE_X_RANGE,
    BANK_RECEIPE_X_RANGE,
)
from EzreD2Shared.shared.consts.adaptative.positions import (
    BANK_CLEAR_SEARCH_IN_POSITION,
    BANK_POSSIBLE_RECEIPE_ICON_POSITION,
    BANK_SEARCH_IN_POSITION,
    BANK_SEARCH_RECIPE_POSITION,
)
from EzreD2Shared.shared.consts.object_configs import ObjectConfigs
from EzreD2Shared.shared.entities.position import Position
from EzreD2Shared.shared.schemas.item import ItemSchema
from EzreD2Shared.shared.schemas.recipe import RecipeSchema
from EzreD2Shared.shared.schemas.region import RegionSchema
from EzreD2Shared.shared.utils.randomizer import wait
from EzreD2Shared.shared.utils.text_similarity import are_similar_text

from src.bots.dofus.hud.small_bar import get_percentage_inventory_bar_normal
from src.bots.dofus.walker.buildings.bank_buildings import BankBuilding
from src.bots.dofus.walker.maps import get_astrub_bank_map
from src.entities.item import ItemProcessedStatus
from src.image_manager.ocr import get_text_from_image
from src.image_manager.transformation import crop_image
from src.services.character import CharacterService

COUNT_SLOT_RECEIPE_BANK = 5


def get_slot_area_item(img: numpy.ndarray, item_name: str) -> RegionSchema | None:
    """Get corresponding area of target item in list of receipe"""
    for index in range(COUNT_SLOT_RECEIPE_BANK):
        slot_img = crop_image(
            img,
            RegionSchema(
                left=BANK_RECEIPE_TITLE_X_RANGE[0],
                right=BANK_RECEIPE_TITLE_X_RANGE[1],
                top=BANK_RECEIPE_SLOT_INITIAL_Y + BANK_RECEIPE_SLOT_HEIGHT * index,
                bot=BANK_RECEIPE_SLOT_INITIAL_Y
                + BANK_RECEIPE_SLOT_HEIGHT * index
                + BANK_RECEIPE_TITLE_MAX_HEIGHT,
            ),
        )
        title_slot = get_text_from_image(slot_img)

        if are_similar_text(title_slot, item_name):
            return RegionSchema(
                left=BANK_RECEIPE_X_RANGE[0],
                right=BANK_RECEIPE_X_RANGE[1],
                top=BANK_RECEIPE_SLOT_INITIAL_Y + BANK_RECEIPE_SLOT_HEIGHT * index,
                bot=BANK_RECEIPE_SLOT_INITIAL_Y
                + BANK_RECEIPE_SLOT_HEIGHT * (index + 1),
            )

    return None


class BankSystem(BankBuilding):
    def _bank_open_chest(self):
        consult_chest_info = self.wait_on_screen(
            ObjectConfigs.Bank.consult_chest_text,
            force=True,
        )
        self.click(consult_chest_info[0])

    def _bank_transfer_all(self) -> numpy.ndarray:
        pos, _, img = self.wait_on_screen(
            ObjectConfigs.Bank.transfer_icon_out, force=True
        )
        self.click(pos)
        sleep(0.3)
        pos = self.get_position(
            self.capture(), ObjectConfigs.Bank.transfer_all_text, force=True
        )[0]
        self.click(pos)
        wait()
        return img

    def bank_clear_inventory(self) -> numpy.ndarray:
        """go to bank & clear inventory, stay in bank hud

        Returns:
            numpy.ndarray
        """
        assert self.character.lvl >= 10
        self.go_to_bank()
        img = self.capture()

        if self.get_curr_map_info().map == get_astrub_bank_map():
            pos = self.get_position(img, ObjectConfigs.Bank.owl_astrub, force=True)[0]
        else:
            pos = self.get_position(img, ObjectConfigs.Bank.owl_bonta, force=True)[0]

        self.click(pos)
        self._bank_open_chest()
        img = self._bank_transfer_all()
        self.pods = CharacterService.get_max_pods(self.character.id)
        return img

    def bank_get_item(self, item: ItemSchema) -> ItemProcessedStatus:
        """need to be in bank chest interface

        Args:
            img (numpy.ndarray)
            item_name (str): the item name targeted

        Returns:
            ItemProcessedStatus: MAX PROCESSED if character is full pod\n
            PROCESSED if character has all possible related item in inv
            NOT PROCESSED if character did not take any related item
        """

        self.send_text(item.name, pos=BANK_SEARCH_IN_POSITION)
        sleep(1)
        pos_item = self.search_icon_item(item, self.capture())
        if pos_item:
            with self.hold(win32con.VK_CONTROL):
                self.click(pos_item, count=2)
            wait()
            if get_percentage_inventory_bar_normal(self.capture()) > 0.9:
                return ItemProcessedStatus.MAX_PROCESSED

            self.click(BANK_CLEAR_SEARCH_IN_POSITION)
            return ItemProcessedStatus.PROCESSED

        self.click(BANK_CLEAR_SEARCH_IN_POSITION)
        sleep(0.3)
        return ItemProcessedStatus.NOT_PROCESSED

    def __get_transfer_position_if_available(
        self, img: numpy.ndarray, slot_area: RegionSchema
    ) -> Position | None:
        """get transfer position, return None if check icon is found,
        Need to be on bank receipe list

        Args:
            img (numpy.ndarray)
            slot_area (Area): the area of the slot targeted

        Returns:
            Position | None: transfer_icon_position
        """

        slot_img = crop_image(img, slot_area)

        if self.get_position(slot_img, ObjectConfigs.Check.small) is not None:
            return None

        position_transfer_in_info = self.get_position(
            slot_img, ObjectConfigs.Bank.transfer_icon_in
        )
        if position_transfer_in_info is not None:
            return Position(
                x_pos=position_transfer_in_info[0].x_pos + slot_area.left,
                y_pos=position_transfer_in_info[0].y_pos + slot_area.top,
            )
        return None

    def bank_get_ingredients_item(self, recipe: RecipeSchema) -> ItemProcessedStatus:
        """need to be in bank chest interface

        Args:
            item_craft (ItemCraftInfo): the target item to pick ingredients

        Returns:
            ItemCraftStatus: did we get full ingredients or not or not at all
        """

        self.click(BANK_POSSIBLE_RECEIPE_ICON_POSITION)

        self.wait_on_screen(ObjectConfigs.Text.receipe)
        self.send_text(recipe.result_item.name, pos=BANK_SEARCH_RECIPE_POSITION)
        img = self.capture()
        if (slot_area := get_slot_area_item(img, recipe.result_item.name)) and (
            transfer_icon_position := self.__get_transfer_position_if_available(
                img, slot_area
            )
        ):
            # we can pick atleast ingredients for one of that item
            self.click(transfer_icon_position)
            if (max_craft_round := (self.pods // recipe.receipe_pod_cost)) < (
                max_craft_total := int(self.get_selected_text())
            ):
                self.send_text("0" + str(max_craft_round))
                self.pods -= max_craft_round * recipe.receipe_pod_cost
                item_craft_status = ItemProcessedStatus.PROCESSED
            else:
                # we got the max possible craft for this item
                self.pods -= max_craft_total * recipe.receipe_pod_cost
                item_craft_status = ItemProcessedStatus.MAX_PROCESSED
                self.key(win32con.VK_RETURN)
            wait()

            img = self.capture()
            if get_percentage_inventory_bar_normal(self.capture()) > 0.9:
                # transfer impossible, we are full pods
                self.pods = 0
                item_craft_status = ItemProcessedStatus.PROCESSED
        else:
            item_craft_status = ItemProcessedStatus.NOT_PROCESSED

        self.click(BANK_POSSIBLE_RECEIPE_ICON_POSITION)
        return item_craft_status

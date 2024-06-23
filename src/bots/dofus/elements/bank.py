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
from src.bots.dofus.walker.core_walker_system import CoreWalkerSystem
from src.bots.dofus.walker.maps import get_astrub_bank_map
from src.entities.item import ItemProcessedStatus
from src.image_manager.ocr import get_text_from_image
from src.image_manager.screen_objects.icon_searcher import IconSearcher
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.image_manager.transformation import crop_image
from src.services.character import CharacterService
from src.services.session import ServiceSession
from src.states.character_state import CharacterState
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller

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


class BankSystem:
    def __init__(
        self,
        bank_building: BankBuilding,
        object_searcher: ObjectSearcher,
        capturer: Capturer,
        image_manager: ImageManager,
        icon_searcher: IconSearcher,
        controller: Controller,
        service: ServiceSession,
        core_walker_sys: CoreWalkerSystem,
        character_state: CharacterState,
    ) -> None:
        self.bank_building = bank_building
        self.capturer = capturer
        self.icon_searcher = icon_searcher
        self.object_searcher = object_searcher
        self.core_walker_sys = core_walker_sys
        self.image_manager = image_manager
        self.controller = controller
        self.service = service
        self.character_state = character_state

    def _bank_open_chest(self):
        consult_chest_info = self.image_manager.wait_on_screen(
            ObjectConfigs.Bank.consult_chest_text,
            force=True,
        )
        self.controller.click(consult_chest_info[0])

    def _bank_transfer_all(self) -> numpy.ndarray:
        pos, _, img = self.image_manager.wait_on_screen(
            ObjectConfigs.Bank.transfer_icon_out, force=True
        )
        self.controller.click(pos)
        sleep(0.3)
        pos = self.object_searcher.get_position(
            self.capturer.capture(),
            ObjectConfigs.Bank.transfer_all_text,
            force=True,
        )[0]
        self.controller.click(pos)
        wait()
        return img

    def bank_clear_inventory(self) -> numpy.ndarray:
        """go to bank & clear inventory, stay in bank hud

        Returns:
            numpy.ndarray
        """
        assert self.character_state.character.lvl >= 10
        self.bank_building.go_to_bank()
        img = self.capturer.capture()

        if self.core_walker_sys.get_curr_map_info().map == get_astrub_bank_map():
            pos = self.object_searcher.get_position(
                img, ObjectConfigs.Bank.owl_astrub, force=True
            )[0]
        else:
            pos = self.object_searcher.get_position(
                img, ObjectConfigs.Bank.owl_bonta, force=True
            )[0]

        self.controller.click(pos)
        self._bank_open_chest()
        img = self._bank_transfer_all()
        self.character_state.pods = CharacterService.get_max_pods(
            self.service, self.character_state.character.id
        )
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

        self.controller.send_text(item.name, pos=BANK_SEARCH_IN_POSITION)
        sleep(1)
        pos_item = self.icon_searcher.search_icon_item(item, self.capturer.capture())
        if pos_item:
            with self.controller.hold(win32con.VK_CONTROL):
                self.controller.click(pos_item, count=2)
            wait()
            if get_percentage_inventory_bar_normal(self.capturer.capture()) > 0.9:
                return ItemProcessedStatus.MAX_PROCESSED

            self.controller.click(BANK_CLEAR_SEARCH_IN_POSITION)
            return ItemProcessedStatus.PROCESSED

        self.controller.click(BANK_CLEAR_SEARCH_IN_POSITION)
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

        if (
            self.object_searcher.get_position(slot_img, ObjectConfigs.Check.small)
            is not None
        ):
            return None

        position_transfer_in_info = self.object_searcher.get_position(
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

        self.controller.click(BANK_POSSIBLE_RECEIPE_ICON_POSITION)

        self.image_manager.wait_on_screen(ObjectConfigs.Text.receipe)
        self.controller.send_text(
            recipe.result_item.name, pos=BANK_SEARCH_RECIPE_POSITION
        )
        img = self.capturer.capture()
        if (slot_area := get_slot_area_item(img, recipe.result_item.name)) and (
            transfer_icon_position := self.__get_transfer_position_if_available(
                img, slot_area
            )
        ):
            # we can pick atleast ingredients for one of that item
            self.controller.click(transfer_icon_position)
            if (
                max_craft_round := (
                    self.character_state.pods // recipe.receipe_pod_cost
                )
            ) < (max_craft_total := int(self.controller.get_selected_text())):
                self.controller.send_text("0" + str(max_craft_round))
                self.character_state.pods -= max_craft_round * recipe.receipe_pod_cost
                item_craft_status = ItemProcessedStatus.PROCESSED
            else:
                # we got the max possible craft for this item
                self.character_state.pods -= max_craft_total * recipe.receipe_pod_cost
                item_craft_status = ItemProcessedStatus.MAX_PROCESSED
                self.controller.key(win32con.VK_RETURN)
            wait()

            img = self.capturer.capture()
            if get_percentage_inventory_bar_normal(self.capturer.capture()) > 0.9:
                # transfer impossible, we are full pods
                self.character_state.pods = 0
                item_craft_status = ItemProcessedStatus.PROCESSED
        else:
            item_craft_status = ItemProcessedStatus.NOT_PROCESSED

        self.controller.click(BANK_POSSIBLE_RECEIPE_ICON_POSITION)
        return item_craft_status

from dataclasses import dataclass
from logging import Logger

from D2Shared.shared.consts.object_configs import ObjectConfigs
from D2Shared.shared.enums import CategoryEnum
from D2Shared.shared.schemas.item import SellItemInfo
from src.bots.dofus.elements.bank import BankSystem
from src.bots.dofus.elements.sale_hotel import SaleHotelSystem
from src.bots.dofus.hud.hud_system import HudSystem
from src.entities.item import ItemProcessedStatus
from src.image_manager.screen_objects.image_manager import ImageManager
from src.services.character import CharacterService
from src.services.price import PriceService
from src.services.session import ServiceSession
from src.states.character_state import CharacterState
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller


@dataclass
class Seller:
    service: ServiceSession
    character_state: CharacterState
    sale_hotel_sys: SaleHotelSystem
    hud_sys: HudSystem
    bank_system: BankSystem
    logger: Logger
    controller: Controller
    capturer: Capturer
    image_manager: ImageManager

    def sell_inventory(
        self, sell_items_infos: set[SellItemInfo]
    ) -> tuple[list[CategoryEnum], list[int]]:
        """sell all items in order of type sale hotel,

        Returns:
            list[CategoryEnum]: list of sale hotel that were full place
        """
        all_completed_items: list[int] = []
        full_categories: list[CategoryEnum] = []
        for category in set(
            map(lambda elem: elem.item.type_item.category, sell_items_infos)
        ):
            self.sale_hotel_sys.go_to_sale_hotel(category)
            is_full_place, completed_items = (
                self.sale_hotel_sys.sale_hotel_sell_items_inv(sell_items_infos)
            )
            if is_full_place:
                full_categories.append(category)
            all_completed_items.extend(completed_items)
            self.hud_sys.close_modals(
                self.capturer.capture(),
                ordered_configs_to_check=[
                    ObjectConfigs.Cross.black_on_grey,
                    ObjectConfigs.Cross.grey_on_black,
                ],
            )
        return full_categories, all_completed_items

    def get_ordered_items(
        self, sell_items_infos: list[SellItemInfo]
    ) -> list[SellItemInfo]:
        price_items = PriceService.get_price_items(
            self.service,
            [_item_info.item_id for _item_info in sell_items_infos],
            self.character_state.character.server_id,
        )
        return sorted(
            sell_items_infos,
            key=lambda _item_info: (
                id(_item_info.item.type_item.category),
                next(
                    _price.average
                    for _price in price_items
                    if _price.item_id == _item_info.item_id
                ),
            ),
            reverse=True,
        )

    def run_seller(
        self,
        sell_items_infos: list[SellItemInfo],
        _completed_items_ids: set[int] | None = None,
    ):
        if _completed_items_ids is None:
            _completed_items_ids = set()

        self.bank_system.bank_clear_inventory()

        sell_items_infos = self.get_ordered_items(sell_items_infos)

        items_infos_inventory: set[SellItemInfo] = set()
        for item_info in sell_items_infos:
            while True:
                item_processed_status = self.bank_system.bank_get_item(item_info.item)
                if item_processed_status == ItemProcessedStatus.NOT_PROCESSED:
                    self.logger.info("Did not found any item in bank, skipping item")
                    break
                items_infos_inventory.add(item_info)
                if item_processed_status == ItemProcessedStatus.PROCESSED:
                    self.logger.info(
                        "Got all possible related item in inv, go to next item"
                    )
                    break

                self.logger.info("Character is full pods, go sell")
                self.hud_sys.close_modals(
                    self.capturer.capture(),
                    ordered_configs_to_check=[ObjectConfigs.Cross.black_on_grey],
                )
                full_categories, _ = self.sell_inventory(items_infos_inventory)

                if len(full_categories) != 0:
                    self.logger.info(f"{full_categories} are full, filtering items.")
                    remaining_sell_item_infos = [
                        item_info
                        for item_info in sell_items_infos
                        if item_info.item not in _completed_items_ids
                        and item_info.item.type_item.category not in full_categories
                    ]
                    return self.run_seller(
                        remaining_sell_item_infos, _completed_items_ids
                    )

                self.bank_system.bank_clear_inventory()
                items_infos_inventory.clear()

            _completed_items_ids.add(item_info.item_id)

        self.logger.info("Got all items in inventory")
        self.hud_sys.close_modals(
            self.capturer.capture(),
            ordered_configs_to_check=[ObjectConfigs.Cross.black_on_grey],
        )
        _, completed_items = self.sell_inventory(items_infos_inventory)
        _completed_items_ids.update(completed_items)
        CharacterService.remove_bank_items(
            self.service,
            self.character_state.character.id,
            list(_completed_items_ids),
        )

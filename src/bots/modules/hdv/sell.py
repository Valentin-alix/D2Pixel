from EzreD2Shared.shared.consts.object_configs import ObjectConfigs
from EzreD2Shared.shared.enums import CategoryEnum
from EzreD2Shared.shared.schemas.item import ItemSchema

from src.bots.dofus.chat.chat_system import ChatSystem
from src.bots.dofus.elements.sale_hotel import SaleHotelSystem
from src.entities.item import ItemProcessedStatus
from src.services.character import CharacterService


class Seller(SaleHotelSystem, ChatSystem):
    def sell_inventory(
        self, items: set[ItemSchema]
    ) -> tuple[list[CategoryEnum], list[int]]:
        """sell all items in order of type sale hotel,

        Returns:
            list[CategoryEnum]: list of sale hotel that were full place
        """
        all_completed_items: list[int] = []
        full_categories: list[CategoryEnum] = []
        for category in set(map(lambda elem: elem.type_item.category, items)):
            self.go_to_sale_hotel(category)
            is_full_place, completed_items = self.sale_hotel_sell_items_inv(items)
            if is_full_place:
                full_categories.append(category)
            all_completed_items.extend(completed_items)
            self.close_modals(
                self.capture(),
                ordered_configs_to_check=[
                    ObjectConfigs.Cross.sale_hotel_inventory_right
                ],
            )
        return full_categories, all_completed_items

    def run_seller(
        self,
        items: list[ItemSchema],
        all_completed_items_ids: set[int] | None = None,
    ):
        if all_completed_items_ids is None:
            all_completed_items_ids = set()

        self.bank_clear_inventory()

        items_inventory: set[ItemSchema] = set()
        for item in sorted(items, key=lambda elem: id(elem.type_item.category)):
            while True:
                item_processed = self.bank_get_item(item)
                if item_processed == ItemProcessedStatus.NOT_PROCESSED:
                    self.log_info("Did not found any item in bank, skipping item")
                    break
                items_inventory.add(item)
                if item_processed == ItemProcessedStatus.PROCESSED:
                    self.log_info(
                        "Got all possible related item in inv, go to next item"
                    )
                    break

                self.log_info("Character is full pods, go sell")
                self.close_modals(
                    self.capture(),
                    ordered_configs_to_check=[ObjectConfigs.Cross.bank_inventory_right],
                )
                full_categories, _ = self.sell_inventory(items_inventory)

                if len(full_categories) != 0:
                    self.log_info("A sale hotel is full, filtering items.")
                    sellable_items = [
                        item
                        for item in items
                        if item not in all_completed_items_ids
                        and item.type_item.category not in full_categories
                    ]
                    return self.run_seller(sellable_items, all_completed_items_ids)

                self.bank_clear_inventory()
                items_inventory.clear()

            all_completed_items_ids.add(item.id)

        self.log_info("Got all items in inventory")
        self.close_modals(
            self.capture(),
            ordered_configs_to_check=[ObjectConfigs.Cross.bank_inventory_right],
        )
        _, completed_items = self.sell_inventory(items_inventory)
        all_completed_items_ids.update(completed_items)
        CharacterService.remove_bank_items(
            self.character.id, list(all_completed_items_ids)
        )

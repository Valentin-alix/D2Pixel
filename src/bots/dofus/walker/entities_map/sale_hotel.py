from dataclasses import dataclass

from cachetools import cached
from cachetools.keys import hashkey

from D2Shared.shared.consts.adaptative.positions import (
    BONTA_SALE_HOTEL_CONSUMABLE_POSITION,
    BONTA_SALE_HOTEL_RESOURCE_POSITION,
)
from D2Shared.shared.entities.position import Position
from D2Shared.shared.enums import CategoryEnum
from src.bots.dofus.walker.core_walker_system import EntityMap
from src.bots.dofus.walker.maps import (
    get_bonta_sale_hotel_consumable_map,
    get_bonta_sale_hotel_resource_map,
)
from src.services.session import ServiceSession


@dataclass
class SaleHotel(EntityMap):
    position: Position

    def __hash__(self) -> int:
        return f"{str(self.map_info)}_{str(self.position)}".__hash__()


@cached(cache={}, key=lambda _, category: hashkey(category))
def get_sales_hotels_by_category(
    service: ServiceSession, category: CategoryEnum
) -> list[SaleHotel]:
    match category:
        case CategoryEnum.RESOURCES:
            return [
                SaleHotel(
                    map_info=get_bonta_sale_hotel_resource_map(service),
                    position=BONTA_SALE_HOTEL_RESOURCE_POSITION,
                )
            ]
        case CategoryEnum.CONSUMABLES:
            return [
                SaleHotel(
                    map_info=get_bonta_sale_hotel_consumable_map(service),
                    position=BONTA_SALE_HOTEL_CONSUMABLE_POSITION,
                )
            ]
        case _:
            raise ValueError(f"Invalid sale hotel  : {category}")

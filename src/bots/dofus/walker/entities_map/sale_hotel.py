from cachetools import cached
from cachetools.keys import hashkey
from pydantic import ConfigDict

from D2Shared.shared.consts.adaptative.positions import (
    ASTRUB_SALE_HOTEL_CONSUMABLE_POSITION,
    ASTRUB_SALE_HOTEL_RESOURCE_POSITION,
    BONTA_SALE_HOTEL_CONSUMABLE_POSITION,
    BONTA_SALE_HOTEL_RESOURCE_POSITION,
)
from D2Shared.shared.entities.position import Position
from D2Shared.shared.enums import CategoryEnum
from src.bots.dofus.walker.core_walker_system import EntityMap
from src.bots.dofus.walker.maps import (
    get_astrub_sale_hotel_consumable_map,
    get_astrub_sale_hotel_resource_map,
    get_bonta_sale_hotel_consumable_map,
    get_bonta_sale_hotel_resource_map,
)
from src.services.session import ServiceSession


class SaleHotel(EntityMap):
    model_config = ConfigDict(frozen=True)

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
                ),
                SaleHotel(
                    map_info=get_astrub_sale_hotel_resource_map(service),
                    position=ASTRUB_SALE_HOTEL_RESOURCE_POSITION,
                ),
            ]
        case CategoryEnum.CONSUMABLES:
            return [
                SaleHotel(
                    map_info=get_bonta_sale_hotel_consumable_map(service),
                    position=BONTA_SALE_HOTEL_CONSUMABLE_POSITION,
                ),
                SaleHotel(
                    map_info=get_astrub_sale_hotel_consumable_map(service),
                    position=ASTRUB_SALE_HOTEL_CONSUMABLE_POSITION,
                ),
            ]
        case _:
            raise ValueError(f"Invalid sale hotel  : {category}")

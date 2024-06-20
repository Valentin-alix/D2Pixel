from functools import cache

from EzreD2Shared.shared.consts.maps import (
    ASTRUB_BANK_MAP_ID,
    ASTRUB_SALE_HOTEL_CONSUMABLE_MAP_ID,
    ASTRUB_SALE_HOTEL_RESOURCE_MAP_ID,
    BONTA_BANK_MAP_ID,
    BONTA_SALE_HOTEL_CONSUMABLE_MAP_ID,
    BONTA_SALE_HOTEL_RESOURCE_MAP_ID,
    BONTA_WORKSHOP_ALCHEMIST_MAP_ID,
    BONTA_WORKSHOP_FISHER_MAP_ID,
    BONTA_WORKSHOP_PEASANT_MAP_ID,
    BONTA_WORKSHOP_WOODCUTTER_MAP_ID,
    BONTA_ZAAP_MAP_ID,
    PORTAL_MAP_INCARNAM_ID,
    PORTAL_MAP_TWELVE_ID,
)
from EzreD2Shared.shared.schemas.map import MapSchema

from src.services.map import MapService


@cache
def get_bonta_workshop_woodcutter_map() -> MapSchema:
    return MapService.get_map(BONTA_WORKSHOP_WOODCUTTER_MAP_ID)


@cache
def get_bonta_workshop_fisher_map() -> MapSchema:
    return MapService.get_map(BONTA_WORKSHOP_FISHER_MAP_ID)


@cache
def get_bonta_workshop_peasant_map() -> MapSchema:
    return MapService.get_map(BONTA_WORKSHOP_PEASANT_MAP_ID)


@cache
def get_bonta_workshop_alchemist_map() -> MapSchema:
    return MapService.get_map(BONTA_WORKSHOP_ALCHEMIST_MAP_ID)


@cache
def get_bonta_sale_hotel_resource_map() -> MapSchema:
    return MapService.get_map(BONTA_SALE_HOTEL_RESOURCE_MAP_ID)


@cache
def get_bonta_sale_hotel_consumable_map() -> MapSchema:
    return MapService.get_map(BONTA_SALE_HOTEL_CONSUMABLE_MAP_ID)


@cache
def get_astrub_sale_hotel_resource_map() -> MapSchema:
    return MapService.get_map(ASTRUB_SALE_HOTEL_RESOURCE_MAP_ID)


@cache
def get_astrub_sale_hotel_consumable_map() -> MapSchema:
    return MapService.get_map(ASTRUB_SALE_HOTEL_CONSUMABLE_MAP_ID)


@cache
def get_bonta_bank_map() -> MapSchema:
    return MapService.get_map(BONTA_BANK_MAP_ID)


@cache
def get_astrub_bank_map() -> MapSchema:
    return MapService.get_map(ASTRUB_BANK_MAP_ID)


@cache
def get_bonta_zaap_map() -> MapSchema:
    return MapService.get_map(BONTA_ZAAP_MAP_ID)


@cache
def get_portal_map_twelve() -> MapSchema:
    return MapService.get_map(PORTAL_MAP_TWELVE_ID)


@cache
def get_portal_map_incarnam() -> MapSchema:
    return MapService.get_map(PORTAL_MAP_INCARNAM_ID)


@cache
def get_portal_map_id_by_world() -> dict[tuple[int, int], MapSchema]:
    portal_map_by_world: dict[tuple[int, int], MapSchema] = {
        (2, 1): get_portal_map_twelve(),
        (1, 2): get_portal_map_incarnam(),
    }
    return portal_map_by_world

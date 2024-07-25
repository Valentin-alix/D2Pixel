from cachetools import cached
from cachetools.keys import hashkey

from D2Shared.shared.consts.maps import (
    ASTRUB_BANK_MAP_CN,
    BONTA_BANK_MAP_CN,
    BONTA_SALE_HOTEL_CONSUMABLE_MAP_CN,
    BONTA_SALE_HOTEL_RESOURCE_MAP_CN,
    BONTA_WORKSHOP_ALCHEMIST_MAP_CN,
    BONTA_WORKSHOP_FISHER_MAP_CN,
    BONTA_WORKSHOP_PEASANT_MAP_CN,
    BONTA_WORKSHOP_WOODCUTTER_MAP_CN,
    BONTA_ZAAP_MAP_CN,
    PORTAL_MAP_INCARNAM_CN,
    PORTAL_MAP_TWELVE_CN,
)
from D2Shared.shared.schemas.map import MapSchema
from src.services.client_service import ClientService
from src.services.map import MapService


@cached(cache={}, key=lambda _: hashkey())
def get_bonta_workshop_woodcutter_map(service: ClientService) -> MapSchema:
    return MapService.get_related_map(service, BONTA_WORKSHOP_WOODCUTTER_MAP_CN)


@cached(cache={}, key=lambda _: hashkey())
def get_bonta_workshop_fisher_map(service: ClientService) -> MapSchema:
    return MapService.get_related_map(service, BONTA_WORKSHOP_FISHER_MAP_CN)


@cached(cache={}, key=lambda _: hashkey())
def get_bonta_workshop_peasant_map(service: ClientService) -> MapSchema:
    return MapService.get_related_map(service, BONTA_WORKSHOP_PEASANT_MAP_CN)


@cached(cache={}, key=lambda _: hashkey())
def get_bonta_workshop_alchemist_map(service: ClientService) -> MapSchema:
    return MapService.get_related_map(service, BONTA_WORKSHOP_ALCHEMIST_MAP_CN)


@cached(cache={}, key=lambda _: hashkey())
def get_bonta_sale_hotel_resource_map(service: ClientService) -> MapSchema:
    return MapService.get_related_map(service, BONTA_SALE_HOTEL_RESOURCE_MAP_CN)


@cached(cache={}, key=lambda _: hashkey())
def get_bonta_sale_hotel_consumable_map(service: ClientService) -> MapSchema:
    return MapService.get_related_map(service, BONTA_SALE_HOTEL_CONSUMABLE_MAP_CN)


@cached(cache={}, key=lambda _: hashkey())
def get_bonta_bank_map(service: ClientService) -> MapSchema:
    return MapService.get_related_map(service, BONTA_BANK_MAP_CN)


@cached(cache={}, key=lambda _: hashkey())
def get_astrub_bank_map(service: ClientService) -> MapSchema:
    return MapService.get_related_map(service, ASTRUB_BANK_MAP_CN)


@cached(cache={}, key=lambda _: hashkey())
def get_bonta_zaap_map(service: ClientService) -> MapSchema:
    return MapService.get_related_map(service, BONTA_ZAAP_MAP_CN)


@cached(cache={}, key=lambda _: hashkey())
def get_portal_map_twelve(service: ClientService) -> MapSchema:
    return MapService.get_related_map(service, PORTAL_MAP_TWELVE_CN)


@cached(cache={}, key=lambda _: hashkey())
def get_portal_map_incarnam(service: ClientService) -> MapSchema:
    return MapService.get_related_map(service, PORTAL_MAP_INCARNAM_CN)


@cached(cache={}, key=lambda _: hashkey())
def get_portal_map_id_by_world(
    service: ClientService,
) -> dict[tuple[int, int], MapSchema]:
    portal_map_by_world: dict[tuple[int, int], MapSchema] = {
        (2, 1): get_portal_map_twelve(service),
        (1, 2): get_portal_map_incarnam(service),
    }
    return portal_map_by_world

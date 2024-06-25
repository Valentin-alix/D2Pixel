from EzreD2Shared.shared.consts.adaptative.positions import (
    ZAAPI_SALE_HOTEL_CATEGORY_POSITION,
    ZAAPI_VARIOUS_CATEGORY_POSITION,
    ZAAPI_WORKSHOP_CATEGORY_POSITION,
)
from EzreD2Shared.shared.entities.position import Position
from EzreD2Shared.shared.enums import CategoryZaapiEnum


def get_position_by_zaapi_category(category_zaapi: CategoryZaapiEnum) -> Position:
    match category_zaapi:
        case CategoryZaapiEnum.WORKSHOP:
            return ZAAPI_WORKSHOP_CATEGORY_POSITION
        case CategoryZaapiEnum.SALE_HOTEL:
            return ZAAPI_SALE_HOTEL_CATEGORY_POSITION
        case CategoryZaapiEnum.VARIOUS:
            return ZAAPI_VARIOUS_CATEGORY_POSITION

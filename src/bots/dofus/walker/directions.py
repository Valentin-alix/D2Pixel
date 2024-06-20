from EzreD2Shared.shared.consts.adaptative.positions import (
    BOTTOM_LEFT_MAP_CHANGE_POSITION,
    BOTTOM_MAP_CHANGE_POSITION,
    BOTTOM_RIGHT_MAP_CHANGE_POSITION,
    LEFT_BOT_MAP_CHANGE_POSITION,
    LEFT_MAP_CHANGE_POSITION,
    LEFT_TOP_MAP_CHANGE_POSITION,
    RIGHT_BOT_MAP_CHANGE_POSITION,
    RIGHT_MAP_CHANGE_POSITION,
    RIGHT_TOP_MAP_CHANGE_POSITION,
    TOP_MAP_CHANGE_POSITION,
    TOP_MAP_LEFT_CHANGE_POSITION,
    TOP_MAP_RIGHT_CHANGE_POSITION,
)
from EzreD2Shared.shared.entities.position import Position
from EzreD2Shared.shared.enums import FromDirection, ToDirection


def get_pos_to_direction(direction: ToDirection) -> Position:
    match direction:
        case ToDirection.LEFT_TOP:
            return LEFT_TOP_MAP_CHANGE_POSITION
        case ToDirection.LEFT:
            return LEFT_MAP_CHANGE_POSITION
        case ToDirection.LEFT_BOT:
            return LEFT_BOT_MAP_CHANGE_POSITION

        case ToDirection.RIGHT_TOP:
            return RIGHT_TOP_MAP_CHANGE_POSITION
        case ToDirection.RIGHT:
            return RIGHT_MAP_CHANGE_POSITION
        case ToDirection.RIGHT_BOT:
            return RIGHT_BOT_MAP_CHANGE_POSITION

        case ToDirection.TOP_LEFT:
            return TOP_MAP_LEFT_CHANGE_POSITION
        case ToDirection.TOP:
            return TOP_MAP_CHANGE_POSITION
        case ToDirection.TOP_RIGHT:
            return TOP_MAP_RIGHT_CHANGE_POSITION

        case ToDirection.BOT_LEFT:
            return BOTTOM_RIGHT_MAP_CHANGE_POSITION
        case ToDirection.BOT:
            return BOTTOM_MAP_CHANGE_POSITION
        case ToDirection.BOT_RIGHT:
            return BOTTOM_LEFT_MAP_CHANGE_POSITION


def get_pos_from_direction(direction: FromDirection) -> Position | None:
    match direction:
        case FromDirection.LEFT_TOP:
            return LEFT_TOP_MAP_CHANGE_POSITION
        case FromDirection.LEFT:
            return LEFT_MAP_CHANGE_POSITION
        case FromDirection.LEFT_BOT:
            return LEFT_BOT_MAP_CHANGE_POSITION

        case FromDirection.RIGHT_TOP:
            return RIGHT_TOP_MAP_CHANGE_POSITION
        case FromDirection.RIGHT:
            return RIGHT_MAP_CHANGE_POSITION
        case FromDirection.RIGHT_BOT:
            return RIGHT_BOT_MAP_CHANGE_POSITION

        case FromDirection.TOP_LEFT:
            return TOP_MAP_LEFT_CHANGE_POSITION
        case FromDirection.TOP:
            return TOP_MAP_CHANGE_POSITION
        case FromDirection.TOP_RIGHT:
            return TOP_MAP_RIGHT_CHANGE_POSITION

        case FromDirection.BOT_LEFT:
            return BOTTOM_RIGHT_MAP_CHANGE_POSITION
        case FromDirection.BOT:
            return BOTTOM_MAP_CHANGE_POSITION
        case FromDirection.BOT_RIGHT:
            return BOTTOM_LEFT_MAP_CHANGE_POSITION
        case _:
            return None

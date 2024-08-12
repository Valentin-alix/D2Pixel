from D2Shared.shared.consts.adaptative.positions import (
    BOTTOM_MAP_CHANGE_POSITION,
    LEFT_MAP_CHANGE_POSITION,
    RIGHT_MAP_CHANGE_POSITION,
    TOP_MAP_CHANGE_POSITION,
)
from D2Shared.shared.entities.position import Position
from D2Shared.shared.enums import Direction


def get_pos_to_direction(direction: Direction) -> Position:
    match direction:
        case Direction.LEFT:
            return LEFT_MAP_CHANGE_POSITION
        case Direction.RIGHT:
            return RIGHT_MAP_CHANGE_POSITION
        case Direction.TOP:
            return TOP_MAP_CHANGE_POSITION
        case Direction.BOT:
            return BOTTOM_MAP_CHANGE_POSITION

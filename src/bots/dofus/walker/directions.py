import random
from D2Shared.shared.consts.adaptative.positions import (
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
from D2Shared.shared.entities.position import Position
from D2Shared.shared.enums import Direction


def get_pos_to_direction(direction: Direction) -> Position:
    match direction:
        case Direction.LEFT:
            return random.choice(
                [
                    LEFT_TOP_MAP_CHANGE_POSITION,
                    LEFT_MAP_CHANGE_POSITION,
                    LEFT_BOT_MAP_CHANGE_POSITION,
                ]
            )
        case Direction.RIGHT:
            return random.choice(
                [
                    RIGHT_TOP_MAP_CHANGE_POSITION,
                    RIGHT_MAP_CHANGE_POSITION,
                    RIGHT_BOT_MAP_CHANGE_POSITION,
                ]
            )
        case Direction.TOP:
            return random.choice(
                [
                    TOP_MAP_LEFT_CHANGE_POSITION,
                    TOP_MAP_CHANGE_POSITION,
                    TOP_MAP_RIGHT_CHANGE_POSITION,
                ]
            )
        case Direction.BOT:
            return random.choice(
                [
                    BOTTOM_LEFT_MAP_CHANGE_POSITION,
                    BOTTOM_MAP_CHANGE_POSITION,
                    BOTTOM_RIGHT_MAP_CHANGE_POSITION,
                ]
            )

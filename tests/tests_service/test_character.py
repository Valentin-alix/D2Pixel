from logging import Logger
import os
import sys
import unittest
from pathlib import Path


from EzreD2Shared.shared.consts.maps import (
    ASTRUB_BANK_MAP_ID,
    BONTA_WORKSHOP_WOODCUTTER_MAP_ID,
)
from EzreD2Shared.shared.enums import FromDirection
from src.gui.signals.app_signals import AppSignals
from src.services.character import CharacterService
from src.services.item import ItemService
from src.services.map import MapService
from src.services.recipe import RecipeService
from src.services.session import ServiceSession

sys.path.append(os.path.join(Path(__file__).parent.parent.parent))


class TestServiceCharacter(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ServiceSession(Logger("temp"), AppSignals())
        self.character = CharacterService.get_or_create_character(self.service, "temp")
        return super().setUp()

    def test_map(self):
        map = MapService.get_map_from_hud(
            self.service, "temp", 14419205, ["-16", "-24"]
        )
        print(map.waypoint)

    def test_get_or_create(self):
        items = CharacterService.get_possible_collectable(
            self.service, self.character.id
        )
        CharacterService.add_bank_items(
            self.service, self.character.id, [elem.item_id for elem in items]
        )
        recipes = RecipeService.get_default_recipes(self.service, self.character.id)
        for recipe in recipes:
            print(recipe.result_item.name)

        sell_items = ItemService.get_default_sellable_items(
            self.service, self.character.id, [elem.id for elem in recipes]
        )
        print(sell_items)

    def test_astar(self):
        path = MapService.find_path(
            self.service,
            True,
            True,
            ASTRUB_BANK_MAP_ID,
            FromDirection.UNKNOWN,
            [],
            [BONTA_WORKSHOP_WOODCUTTER_MAP_ID],
        )
        print(path)

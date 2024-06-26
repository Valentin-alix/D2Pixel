from logging import Logger
import os
import sys
import unittest
from pathlib import Path


from src.gui.signals.app_signals import AppSignals
from src.services.character import CharacterService
from src.services.item import ItemService
from src.services.recipe import RecipeService
from src.services.session import ServiceSession

sys.path.append(os.path.join(Path(__file__).parent.parent.parent))


class TestServiceCharacter(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_get_or_create(self):
        service = ServiceSession(Logger("temp"), AppSignals())

        character = CharacterService.get_or_create_character(service, "temp")
        items = CharacterService.get_possible_collectable(service, character.id)
        CharacterService.add_bank_items(
            service, character.id, [elem.item_id for elem in items]
        )
        recipes = RecipeService.get_default_recipes(service, character.id)
        for recipe in recipes:
            print(recipe.result_item.name)

        sell_items = ItemService.get_default_sellable_items(
            service, character.id, [elem.id for elem in recipes]
        )
        print(sell_items)

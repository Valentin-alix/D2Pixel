import os
import sys
import unittest
from pathlib import Path

from EzreD2Shared.shared.enums import BreedEnum

from src.services.character import CharacterService
from src.services.collectable import CollectableService

sys.path.append(os.path.join(Path(__file__).parent.parent.parent))


class TestServiceCharacter(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_get_or_create(self):
        character = CharacterService.get_or_create_character("temp")
        character.lvl = 189
        character.breed_id = BreedEnum.ENU

        possible = CharacterService.get_possible_collectable(character.id)
        print(possible)
        on_map = CollectableService.get_possible_config_on_map(  # FIXME
            189531649, [elem.id for elem in possible]
        )
        print(on_map)

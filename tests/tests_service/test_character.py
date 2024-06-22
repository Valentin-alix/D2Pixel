import os
import sys
import unittest
from pathlib import Path


from src.services.breed import BreedService

sys.path.append(os.path.join(Path(__file__).parent.parent.parent))


class TestServiceCharacter(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_get_or_create(self):
        breeds = BreedService.get_breeds()
        print(breeds)

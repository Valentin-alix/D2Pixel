import unittest

from src.data_layer.database import SessionLocal
from src.data_layer.models.job import HARVEST_JOBS_ID
from src.data_layer.queries.recipe import get_recipes_to_upgrade_jobs
from src.data_layer.states.character_state import CharacterState


class TestQueries(unittest.TestCase):
    def setUp(self) -> None:
        self.character_state = CharacterState("temp")

        return super().setUp()

    def test_recipes_upgrade_jobs(self):
        for job_id in HARVEST_JOBS_ID:
            self.character_state.character.set_character_job_lvl(job_id, 60)

        possible_collectable = self.character_state.character.get_possible_collectable(
            SessionLocal()
        )
        print(possible_collectable)
        self.character_state.character.bank_items.extend(
            (elem.item for elem in possible_collectable)
        )
        SessionLocal.commit()

        temp = get_recipes_to_upgrade_jobs(
            SessionLocal(), self.character_state.character
        )
        print(temp)

import os
import sys
import unittest
from logging import Logger
from pathlib import Path

from src.services.item import ItemService
from src.services.sub_area import SubAreaService

sys.path.append(os.path.join(Path(__file__).parent.parent.parent))
from D2Shared.shared.enums import JobEnum
from src.gui.signals.app_signals import AppSignals
from src.services.character import CharacterService
from src.services.recipe import RecipeService
from src.services.session import ServiceSession


class TestServiceCharacter(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ServiceSession(Logger("Xeloreeuu"), AppSignals())
        self.character = CharacterService.get_or_create_character(
            self.service, "Tema-la-ratte"
        )
        # for job_id in HARVEST_JOBS_ID:
        #     CharacterService.update_job_info(
        #         self.service, self.character.id, job_id, 80
        #     )
        return super().setUp()

    def test_icon(self):
        colls = CharacterService.get_possible_collectable(
            self.service, self.character.id
        )
        CharacterService.add_bank_items(
            self.service, self.character.id, [elem.item_id for elem in colls]
        )
        recipes = RecipeService.get_valid_ordered(
            self.service,
            [elem.id for elem in self.character.recipes],
            self.character.id,
        )
        print(recipes)
        items = ItemService.get_default_sellable_items(
            self.service, self.character.id, [elem.id for elem in recipes]
        )
        print(items)

    def test_get_or_create(self):
        for job_info in self.character.jobs_infos:
            if job_info.job.name == JobEnum.ALCHIMIST:
                job_info.lvl = 100
            elif job_info.job.name == JobEnum.PEASANT:
                job_info.lvl = 69
            elif job_info.job.name == JobEnum.WOODCUTTER:
                job_info.lvl = 135
            elif job_info.job.name == JobEnum.FISHERMAN:
                job_info.lvl = 85
        CharacterService.update_job_infos(
            self.service, self.character.id, self.character.jobs_infos
        )

        colls = CharacterService.get_possible_collectable(
            self.service, self.character.id
        )
        CharacterService.add_bank_items(
            self.service, self.character.id, [elem.item_id for elem in colls]
        )

    def test_item(self):
        # before = perf_counter()
        # items = ItemService.get_items(self.service)
        # print(perf_counter() - before)
        # print(len(items))
        valid_sub_ids = [
            _elem.id
            for _elem in SubAreaService.get_valid_sub_areas_harvester(
                self.service, self.character.id
            )
        ]
        temp = SubAreaService.get_max_time_harvester(self.service, valid_sub_ids)
        print(temp)

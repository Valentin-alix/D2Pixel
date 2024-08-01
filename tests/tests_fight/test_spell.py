import os
import unittest
from logging import Logger

import cv2

from src.bots.dofus.fight.grid.grid import Grid
from src.bots.dofus.fight.grid.ldv_grid import LdvGrid
from src.bots.dofus.fight.spells.spell_manager import SpellManager
from src.gui.signals.app_signals import AppSignals
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from src.services.spell import SpellService
from src.states.character_state import CharacterState
from tests.utils import PATH_FIXTURES


class TestSpellsFight(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = Logger("root")
        self.service = ServiceSession(logger=self.logger, app_signals=AppSignals())
        self.character_state = CharacterState(self.service, "temp")
        object_searcher = ObjectSearcher(logger=self.logger, service=self.service)
        self.grid = Grid(logger=self.logger, object_searcher=object_searcher)
        self.ldv_grid = LdvGrid(grid=self.grid)
        self.spell_manager = SpellManager(
            grid=self.grid,
            service=self.service,
            character_state=self.character_state,
        )
        return super().setUp()

    def test_choose_spells(self):
        img = cv2.imread(os.path.join(PATH_FIXTURES, "fight", "turn", "1.png"))
        self.character_state.character.lvl = 60
        self.spell_manager._pa = 14

        self.grid.init_grid(img)
        self.grid.parse_grid(img)
        self.grid.draw_grid(img)

        spells = SpellService.get_best_combination(
            self.service,
            None,
            [],
            [],
            False,
            self.character_state.character_id,
            self.spell_manager._pa,
            {},
            [],
        )

    def test_get_max_dmg(self):
        spell_lvl = self.spell_manager.get_max_range_valuable_dmg_spell()
        print(spell_lvl)

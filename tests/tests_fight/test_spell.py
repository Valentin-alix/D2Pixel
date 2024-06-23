import os
import unittest

import cv2

from src.bots.dofus.fight.spells.spell_manager import SpellManager

# sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from src.data_layer.models.characteristic import CharacteristicEnum
from src.gui.signals.dofus_signals import BotSignals
from src.window_manager.organizer import WindowInfo
from tests.utils import PATH_FIXTURES


class TestSpellsFight(unittest.TestCase):
    def setUp(self) -> None:
        self.spell_manager = SpellManager(
            window_info=WindowInfo(hwnd=1, name="Tema-la-ratte"),
            bot_signals=BotSignals(),
        )
        return super().setUp()

    def test_choose_spells(self):
        img = cv2.imread(os.path.join(PATH_FIXTURES, "fight", "turn", "1.png"))
        self.spell_manager.character.lvl = 60
        self.spell_manager._pa = 14

        self.spell_manager.init_grid(img)
        self.spell_manager.parse_grid(img)
        self.spell_manager.draw_grid(img)

        spells = self.spell_manager.choose_spells(None, [], False)
        for spell in spells:
            print(spell, spell.is_boost_for_characteristic(CharacteristicEnum.PM))

    def test_get_max_dmg(self):
        # TODO Check pos spells
        # self.spell_manager.character.lvl = 80

        spell_lvls = self.spell_manager.character.get_spells_levels
        for spell_lvl in spell_lvls:
            print(spell_lvl)

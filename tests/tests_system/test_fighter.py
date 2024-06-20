import unittest
from time import sleep

from src.bots.dofus.fight.fight_system import FightSystem
from src.data_layer.consts.object_configs import ObjectConfigs
from tests.tests_system.utils import get_base_params_system


@unittest.skipIf(get_base_params_system().get("window", None) is None, "")
class TestFighterSystem(unittest.TestCase):
    fighter: FightSystem

    def setUp(self) -> None:
        self.fighter = FightSystem(**get_base_params_system())
        return super().setUp()

    def test_fighter(self):
        while True:
            if self.fighter.get_position(
                self.fighter.capture(), ObjectConfigs.Fight.in_fight
            ):
                self.fighter.play_fight()
            sleep(1)

    def test_phenix(self):
        self.fighter.handle_post_fight()

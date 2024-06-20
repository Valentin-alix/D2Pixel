import unittest

from src.bots.dofus.hud.hud_system import HudSystem
from src.data_layer.database import SessionLocal
from tests.tests_system.utils import get_base_params_system


@unittest.skipIf(get_base_params_system().get("window", None) is None, "")
class TestHudSystem(unittest.TestCase):
    hud_sys: HudSystem

    def setUp(self) -> None:
        self.hud_sys = HudSystem(**get_base_params_system(), session=SessionLocal())
        return super().setUp()

    def test_close_modals(self):
        self.hud_sys.clean_interface(self.hud_sys.capture())

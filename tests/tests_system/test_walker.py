import unittest

from src.bots.dofus.walker.core_walker_system import CoreWalkerSystem
from src.data_layer.schemas.map import MapSchema
from tests.tests_system.utils import get_base_params_system


@unittest.skipIf(get_base_params_system().get("window", None) is None, "")
class TestWalkerSystem(unittest.TestCase):
    walker_sys: CoreWalkerSystem

    def setUp(self) -> None:
        self.walker_sys = CoreWalkerSystem(**get_base_params_system())
        return super().setUp()

    def test_travel_world(self):
        self.walker_sys.travel_to_world(2)

    def test_travel_map(self):
        self.walker_sys.travel_to_map(
            [MapSchema(x=0, y=-37).get_force_related_map(self.walker_sys.session)],
            use_transport=False,
        )

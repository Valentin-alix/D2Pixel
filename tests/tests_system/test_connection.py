import unittest

from src.bots.dofus.connection.connection_system import ConnectionSystem
from tests.tests_system.utils import get_base_params_system


@unittest.skipIf(get_base_params_system().get("window", None) is None, "")
class TestConnectionSystem(unittest.TestCase):
    connection: ConnectionSystem

    def setUp(self) -> None:
        self.connection = ConnectionSystem(**get_base_params_system())
        return super().setUp()

    def test_connect(self):
        assert self.connection.connect_character(self.connection.capture()) is True

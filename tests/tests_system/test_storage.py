import unittest

from src.bots.dofus.elements.bank import BankSystem
from src.data_layer.database import SessionLocal
from tests.tests_system.utils import get_base_params_system


@unittest.skipIf(get_base_params_system().get("window", None) is None, "")
class TestStorageSystem(unittest.TestCase):
    def setUp(self) -> None:
        self.bank_sys = BankSystem(**get_base_params_system(), session=SessionLocal())
        return super().setUp()

    def test_clear_inventory(self):
        self.bank_sys.bank_clear_inventory()

    def test_get_item_in_bank(self):
        self.bank_sys.bank_clear_inventory()
        # self.storage_sys.get_item_bank("Queue de prespic")

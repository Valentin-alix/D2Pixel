from logging import Logger
import os
import sys
import unittest
from pathlib import Path


from EzreD2Shared.shared.consts.maps import BONTA_BANK_MAP_ID
from EzreD2Shared.shared.enums import FromDirection
from src.gui.signals.app_signals import AppSignals
from src.services.map import MapService
from src.services.session import ServiceSession

sys.path.append(os.path.join(Path(__file__).parent.parent.parent))


class TestServiceCharacter(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_get_or_create(self):
        service = ServiceSession(Logger("temp"), AppSignals())

        paths = MapService.find_path(
            service, True, True, 212730627, FromDirection.LEFT, [], [BONTA_BANK_MAP_ID]
        )
        print(paths)

import os
import unittest

import cv2

from src.bots.dofus.elements.bank import get_slot_area_item
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_BANK = os.path.join(PATH_FIXTURES, "hud", "bank")


class TestBank(unittest.TestCase):
    def test_bank_receipe_title_text(self):
        BANK_RECEIPE_FOLDER = os.path.join(PATH_FIXTURES_BANK, "receipe")

        ITEMS_BY_FILENAME: dict[str, list[str]] = {
            "1": ["Planche à griller", "Substrat de Bocage"],
            "2": [
                "Potion des ancêtres",
                "Planche à griller",
                "Substrat de Bocage",
                "Baton de crabe",
                "Fougasse",
            ],
        }

        for filename in os.listdir(BANK_RECEIPE_FOLDER):
            img = cv2.imread(os.path.join(BANK_RECEIPE_FOLDER, filename))
            for item in ITEMS_BY_FILENAME[filename[:-4]]:
                area = get_slot_area_item(img, item)
                assert area is not None, area

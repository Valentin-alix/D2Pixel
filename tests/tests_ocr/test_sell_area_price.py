import os
import unittest

import cv2

from src.bots.dofus.elements.sale_hotel import (
    sale_hotel_get_current_quantity_item,
    sale_hotel_get_price_average_item,
    sale_hotel_get_price_item,
)
from tests.utils import PATH_FIXTURES

SALE_HOTEL_PRICE_FOLDER = os.path.join(
    PATH_FIXTURES, "hud", "sale_hotel", "sale_hotel_price"
)


class TestGetAreaPriceItem(unittest.TestCase):
    def test_quantiy(self):
        QUANTITY_BY_FILENAME: dict[str, int] = {
            "1": 100,
            "2": 10,
            "3": 1,
            "4": 10,
            "5": 100,
        }

        for filename in os.listdir(SALE_HOTEL_PRICE_FOLDER):
            img = cv2.imread(os.path.join(SALE_HOTEL_PRICE_FOLDER, filename))
            quantity = sale_hotel_get_current_quantity_item(img)
            assert quantity == QUANTITY_BY_FILENAME[filename[:-4]]

    def test_price_item(self):
        PRICE_BY_FILENAME: dict[str, int] = {
            "1": 799990,
            "2": 34866,
            "3": 23,
            "4": 377,
            "5": 1785,
            "6": 10,
        }

        for index, filename in enumerate(os.listdir(SALE_HOTEL_PRICE_FOLDER)):
            img = cv2.imread(os.path.join(SALE_HOTEL_PRICE_FOLDER, filename))
            price = sale_hotel_get_price_item(img, 100)
            # print(price)
            print(sale_hotel_get_price_average_item(img))
            assert price is not None
            assert price[0] == PRICE_BY_FILENAME[filename[:-4]]

import os
import unittest
from logging import Logger

import cv2

from src.bots.dofus.elements.sale_hotel import SaleHotel
from tests.utils import PATH_FIXTURES

SALE_HOTEL_PRICE_FOLDER = os.path.join(
    PATH_FIXTURES, "hud", "sale_hotel", "sale_hotel_price"
)


class TestGetAreaPriceItem(unittest.TestCase):
    def setUp(self) -> None:
        self.sale_hotel = SaleHotel(Logger(name="root"))
        return super().setUp()

    def test_quantiy(self):
        QUANTITY_BY_FILENAME: dict[str, int] = {
            "1": 100,
            "2": 10,
            "3": 1,
            "4": 10,
            "5": 100,
            "6": 1,
            "7": 100,
        }

        for filename in os.listdir(SALE_HOTEL_PRICE_FOLDER):
            img = cv2.imread(os.path.join(SALE_HOTEL_PRICE_FOLDER, filename))
            quantity = self.sale_hotel.sale_hotel_get_current_quantity_item(img)
            print(quantity)
            assert quantity == QUANTITY_BY_FILENAME[filename[:-4]]

    def test_price_item(self):
        # FIXME area price by quantity
        PRICE_BY_FILENAME: dict[str, int] = {
            "1": 799990,
            "2": 34866,
            "3": 23,
            "4": 377,
            "5": 1785,
            "6": 147,
            "7": 6575,
            "8": 42884,
        }

        for index, filename in enumerate(os.listdir(SALE_HOTEL_PRICE_FOLDER)):
            img = cv2.imread(os.path.join(SALE_HOTEL_PRICE_FOLDER, filename))
            price = self.sale_hotel.sale_hotel_get_price_item(img, 100)
            # print(price)
            print(index, price)
            # print(self.sale_hotel.sale_hotel_get_price_average_item(img))
            assert price is not None
            assert price[0] == PRICE_BY_FILENAME[filename[:-4]]

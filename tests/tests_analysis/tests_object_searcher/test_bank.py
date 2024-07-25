import os
import unittest
from logging import Logger

import cv2

from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.client_service import ClientService
from tests.utils import PATH_FIXTURES


class TestBank(unittest.TestCase):
    def setUp(self):
        service_session = ClientService(Logger("root"))
        self.object_searcher = ObjectSearcher(service_session)

    def test_position_bank_door(self):
        path_img = os.path.join(PATH_FIXTURES, "objects", "bank_door.png")
        img = cv2.imread(path_img)

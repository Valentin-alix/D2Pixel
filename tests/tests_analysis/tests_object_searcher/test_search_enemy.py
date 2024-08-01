import os
import unittest
from logging import Logger

import cv2

from D2Shared.shared.consts.object_configs import ObjectConfigs
from src.gui.signals.app_signals import AppSignals
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_FIGHT_ENEMY = os.path.join(PATH_FIXTURES, "fight")


class TestSearchEnemy(unittest.TestCase):
    def setUp(self):
        logger = Logger("root")
        service = ServiceSession(logger, AppSignals())
        self.object_searcher = ObjectSearcher(logger=logger, service=service)

    def test_back(self):
        DIRECTORY_ENEMY_BACK = os.path.join(PATH_FIXTURES_FIGHT_ENEMY, "enemy", "back")
        for filename in os.listdir(DIRECTORY_ENEMY_BACK):
            img = cv2.imread(os.path.join(DIRECTORY_ENEMY_BACK, filename))
            enemy_position = self.object_searcher.get_position(
                img, ObjectConfigs.Fight.enemy
            )
            assert enemy_position is not None

    def test_front(self):
        DIRECTORY_ENEMY_FRONT = os.path.join(
            PATH_FIXTURES_FIGHT_ENEMY, "enemy", "front"
        )
        for filename in os.listdir(DIRECTORY_ENEMY_FRONT):
            img = cv2.imread(os.path.join(DIRECTORY_ENEMY_FRONT, filename))
            enemy_position = self.object_searcher.get_position(
                img, ObjectConfigs.Fight.enemy
            )
            assert enemy_position is not None

    def test_right(self):
        DIRECTORY_ENEMY_RIGHT = os.path.join(
            PATH_FIXTURES_FIGHT_ENEMY, "enemy", "right"
        )
        for filename in os.listdir(DIRECTORY_ENEMY_RIGHT):
            img = cv2.imread(os.path.join(DIRECTORY_ENEMY_RIGHT, filename))
            enemy_position = self.object_searcher.get_position(
                img, ObjectConfigs.Fight.enemy
            )
            assert enemy_position is not None

    def test_left(self):
        DIRECTORY_ENEMY_LEFT = os.path.join(PATH_FIXTURES_FIGHT_ENEMY, "enemy", "left")
        for filename in os.listdir(DIRECTORY_ENEMY_LEFT):
            if filename != "4.png":
                continue
            img = cv2.imread(os.path.join(DIRECTORY_ENEMY_LEFT, filename))
            enemy_position = self.object_searcher.get_multiple_position(
                img, ObjectConfigs.Fight.enemy
            )
            for info, pos in enemy_position:
                print(pos)
            assert enemy_position is not None

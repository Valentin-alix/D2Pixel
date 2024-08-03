from dataclasses import dataclass

from D2Shared.shared.consts.object_configs import ObjectConfigs
from src.bots.dofus.hud.hud_system import Hud
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.window_manager.capturer import Capturer


@dataclass
class Blocked:
    capturer: Capturer
    object_searcher: ObjectSearcher
    hud: Hud

    def is_blocked_character(self) -> bool:
        """check if character has any interface open or is not in game

        Returns:
            bool: is_blocked
        """
        img = self.capturer.capture()
        if not self.object_searcher.get_position(img, ObjectConfigs.in_game):
            return True

        for config in self.hud.close_interface_configs:
            if self.object_searcher.get_position(img, config):
                return True

        return False

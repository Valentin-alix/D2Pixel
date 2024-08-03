from dataclasses import dataclass
from logging import Logger
from time import perf_counter, sleep
from typing import override

import numpy

from D2Shared.shared.consts.adaptative.regions import INFO_MAP_REGION
from D2Shared.shared.consts.object_configs import ObjectConfigs
from D2Shared.shared.schemas.user import ReadUserSchema
from src.bots.dofus.fight.fight_system import FightSystem
from src.bots.dofus.hud.hud_system import HudSystem
from src.bots.dofus.walker.core_walker_system import (
    CoreWalkerSystem,
    WaitForNewMapWalking,
)
from src.image_manager.animation import AnimationManager
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.session import ServiceSession
from src.states.character_state import CharacterState
from src.states.map_state import MapState
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller


@dataclass
class WalkerSystem(CoreWalkerSystem):
    fight_sys: FightSystem
    hud_sys: HudSystem
    logger: Logger
    map_state: MapState
    character_state: CharacterState
    controller: Controller
    image_manager: ImageManager
    object_searcher: ObjectSearcher
    animation_manager: AnimationManager
    capturer: Capturer
    service: ServiceSession
    user: ReadUserSchema

    @override
    def wait_for_new_map_walking(
        self, args: WaitForNewMapWalking = WaitForNewMapWalking()
    ) -> tuple[numpy.ndarray | None, bool]:
        self.animation_manager._prev_img = self.capturer.capture()

        initial_time = perf_counter()
        was_teleported: bool = False

        sleep(args.retry_args.offset_start)

        while perf_counter() - initial_time < args.retry_args.timeout:
            img = self.capturer.capture()
            if args.extra_func is not None:
                img = args.extra_func(img)

            if (
                self.object_searcher.get_position(img, ObjectConfigs.Fight.in_fight)
                is not None
            ):
                before_fight_time = perf_counter()
                img, was_teleported = self.fight_sys.play_fight()
                self.logger.info(f"Was teleported : {was_teleported}")
                initial_time += perf_counter() - before_fight_time

            if (
                self.animation_manager._is_start_animation(INFO_MAP_REGION, img)
                is not None
            ):
                is_new_map, img = self.on_new_map()
                if is_new_map:
                    return img, was_teleported

            sleep(args.retry_args.repeat_time)

        return None, was_teleported

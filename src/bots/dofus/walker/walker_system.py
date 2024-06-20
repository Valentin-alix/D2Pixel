from time import perf_counter, sleep
from typing import override

import numpy
from EzreD2Shared.shared.consts.adaptative.regions import INFO_MAP_REGION
from EzreD2Shared.shared.consts.object_configs import ObjectConfigs

from src.bots.dofus.fight.fight_system import FightSystem
from src.bots.dofus.walker.core_walker_system import (
    WaitForNewMapWalking,
)


class WalkerSystem(FightSystem):
    @override
    def wait_for_new_map_walking(
        self, args: WaitForNewMapWalking = WaitForNewMapWalking()
    ) -> tuple[numpy.ndarray | None, bool]:
        self._prev_img = self.capture()

        initial_time = perf_counter()
        was_teleported: bool = False

        sleep(args.retry_args.offset_start)

        while perf_counter() - initial_time < args.retry_args.timeout:
            img = self.capture()
            if args.extra_func is not None:
                img = args.extra_func(img)

            if (
                args.check_fight or self.get_curr_map_info().map.allow_monster_fight
            ) and self.get_position(img, ObjectConfigs.Fight.in_fight) is not None:
                before_fight_time = perf_counter()
                img, was_teleported = self.play_fight()
                self.log_info(f"Was teleported : {was_teleported}")
                initial_time += perf_counter() - before_fight_time

            if self._is_start_animation(INFO_MAP_REGION, img) is not None:
                is_new_map, img = self.on_new_map()
                if is_new_map:
                    return img, was_teleported

            sleep(args.retry_args.repeat_time)

        return None, was_teleported

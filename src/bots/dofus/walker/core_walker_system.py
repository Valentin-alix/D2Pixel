from contextlib import nullcontext
from logging import Logger
from typing import Any, Callable, Literal, NamedTuple, Sequence, TypeVar, overload

import numpy
import win32con
from EzreD2Shared.shared.consts.adaptative.positions import (
    PORTAL_INCARNAM_ENTER_POSITION,
    PORTAL_INCARNAM_TAKE_POSITION,
    PORTAL_TWELVE_ACCEPT_POSITION,
    PORTAL_TWELVE_CONFIRM_POSITION,
    PORTAL_TWELVE_TAKE_POSITION,
    SEARCH_ZAAP_POSITION,
    ZAAP_HAVRE_SAC_POSITION,
    ZAAPI_SEARCH_POSITION,
)
from EzreD2Shared.shared.consts.adaptative.regions import INFO_MAP_REGION
from EzreD2Shared.shared.consts.object_configs import ObjectConfigs
from EzreD2Shared.shared.directions import get_inverted_direction
from EzreD2Shared.shared.enums import FromDirection
from EzreD2Shared.shared.schemas.map import BaseMapSchema
from EzreD2Shared.shared.schemas.map_direction import MapDirectionSchema
from EzreD2Shared.shared.schemas.waypoint import WaypointSchema
from EzreD2Shared.shared.schemas.zaapi import ZaapiSchema
from EzreD2Shared.shared.utils.randomizer import RANGE_NEW_MAP, wait

from src.bots.dofus.hud.hud_system import HudSystem
from src.bots.dofus.hud.map import get_map
from src.bots.dofus.walker.directions import (
    get_pos_to_direction,
)
from src.bots.dofus.walker.entities_map.entity_map import EntityMap
from src.bots.dofus.walker.maps import get_portal_map_id_by_world
from src.common.retry import (
    MAX_RETRY,
    RetryTimeArgs,
    retry_count,
    retry_force_count,
)
from src.entities.building_info import BuildingInfo
from src.exceptions import (
    CharacterIsStuckException,
    UnknowStateException,
)
from src.image_manager.animation import AnimationManager
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.character import CharacterService
from src.services.map import MapService
from src.services.session import ServiceSession
from src.services.world import WorldService
from src.states.character_state import CharacterState
from src.states.map_state import CurrentMapInfo, MapState
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller

EntityMapT = TypeVar("EntityMapT", bound=EntityMap)


class WaitForNewMapWalking(NamedTuple):
    retry_args: RetryTimeArgs = RetryTimeArgs(
        offset_start=1, timeout=15, repeat_time=0.5
    )
    extra_func: Callable[[numpy.ndarray], numpy.ndarray] | None = None
    check_fight: bool = False


class CoreWalkerSystem:
    def __init__(
        self,
        hud_sys: HudSystem,
        logger: Logger,
        map_state: MapState,
        character_state: CharacterState,
        controller: Controller,
        image_manager: ImageManager,
        object_searcher: ObjectSearcher,
        animation_manager: AnimationManager,
        capturer: Capturer,
        service: ServiceSession,
    ) -> None:
        self.hud_sys = hud_sys
        self.object_searcher = object_searcher
        self.animation_manager = animation_manager
        self.capturer = capturer
        self.logger = logger
        self.map_state = map_state
        self.character_state = character_state
        self.controller = controller
        self.image_manager = image_manager
        self.service = service

    def on_new_map(self, pause: bool = True) -> tuple[bool, numpy.ndarray]:
        if pause:
            wait(RANGE_NEW_MAP)

        img = self.capturer.capture()
        if self.map_state.curr_map_info:
            from_map = self.map_state.curr_map_info.map
        else:
            from_map = None

        map, text = get_map(self.service, img, from_map)

        if (
            self.map_state.curr_map_info
            and self.map_state.curr_map_info.map == map
            and self.map_state.curr_map_info.zone_text == text
        ):
            return False, img

        if map.waypoint is not None:
            CharacterService.add_waypoint(
                self.service, self.character_state.character.id, map.waypoint.id
            )

        self.map_state.curr_map_info = CurrentMapInfo(map=map, img=img, zone_text=text)
        self.logger.info(f"New map : {self.map_state.curr_map_info}")

        return True, img

    def get_curr_map_info(self) -> CurrentMapInfo:
        if self.map_state.curr_map_info is None:
            self.logger.info("Current map info is None, getting info")
            self.on_new_map(False)
            assert self.map_state.curr_map_info is not None
        return self.map_state.curr_map_info

    def get_curr_direction(self) -> FromDirection:
        if self.map_state.curr_direction is None:
            self.logger.info("Current direction is None, changing map")
            self.change_map()
            assert self.map_state.curr_direction is not None
        return self.map_state.curr_direction

    def init_first_move(
        self,
        img: numpy.ndarray,
        target_maps: Sequence[BaseMapSchema],
        use_transport: bool = True,
        character_waypoints: list[WaypointSchema] | None = None,
    ) -> numpy.ndarray:
        if not self.map_state.is_first_move:
            return img

        self.map_state.is_first_move = False

        if not (self.character_state.character.is_sub and use_transport):
            self.get_curr_direction()
            return img

        near_zaap: WaypointSchema | None = min(
            (
                waypoint
                for waypoint in WorldService.get_waypoints(
                    self.service, self.get_curr_map_info().map.world_id
                )
                if character_waypoints is None or waypoint in character_waypoints
            ),
            key=lambda waypoint: min(
                waypoint.map.get_dist_map(target_map) for target_map in target_maps
            ),
            default=None,
        )
        if near_zaap is not None:
            img = self.use_zaap(near_zaap)
        else:
            self.get_curr_direction()

        return img

    # Transports

    def use_zaap(self, waypoint: WaypointSchema) -> numpy.ndarray:
        character_waypoints = CharacterService.get_waypoints(
            self.service, self.character_state.character.id
        )
        if waypoint not in character_waypoints:
            img = self.travel_to_map([waypoint.map], character_waypoints)
        else:
            if not self.get_curr_map_info().map.allow_teleport_from:
                # get near map that can use havre sac
                near_map_allow_havre = MapService.get_near_map_allow_havre(
                    self.service, self.get_curr_map_info().map.id
                )
                img = self.travel_to_map([near_map_allow_havre])
                return self.use_zaap(waypoint)
            img = self.capturer.capture()
            if (
                self.object_searcher.get_position(
                    img, ObjectConfigs.PathFinding.lotery_havre_sac
                )
                is None
            ):
                new_img: numpy.ndarray | None = None
                for _ in range(2):
                    self.controller.key("h")
                    if (new_img := self.wait_for_new_map()) is not None:
                        break
                if new_img is None:
                    raise UnknowStateException(img, "no_havre_sac")
                img = new_img

            self.controller.click(ZAAP_HAVRE_SAC_POSITION)
            tp_pos, _, img = self.image_manager.wait_on_screen(
                ObjectConfigs.PathFinding.teleport_zaap, force=True
            )

            self.controller.send_text(
                MapService.get_map(self.service, waypoint.map_id).sub_area.name,
                pos=SEARCH_ZAAP_POSITION,
            )

            if (new_img := self.wait_for_new_map()) is None:
                self.controller.click(tp_pos)
                img = self.wait_for_new_map(force=True)
            else:
                img = new_img
            self.map_state.curr_direction = FromDirection.WAYPOINT
            self.map_state.building = None
        return img

    def use_zaapi(self, zaapi: ZaapiSchema) -> numpy.ndarray:
        self.go_out_building()
        position_zaapi = self.object_searcher.get_position(
            self.capturer.capture(),
            ObjectConfigs.PathFinding.zaapi,
            self.get_curr_map_info().map.id,
            force=True,
        )[0]
        self.controller.click(position_zaapi)

        tp_pos, _, img = self.image_manager.wait_on_screen(
            ObjectConfigs.PathFinding.teleport_zaap, force=True
        )
        self.controller.click(zaapi.category.value)
        self.controller.send_text(zaapi.text, pos=ZAAPI_SEARCH_POSITION)

        new_img = self.wait_for_new_map()
        if new_img is None:
            self.controller.click(tp_pos)
            img = self.wait_for_new_map(force=True)
        else:
            img = new_img
        self.map_state.curr_direction = FromDirection.ZAAPI
        return self.hud_sys.close_modals(
            img, [ObjectConfigs.Cross.bank_inventory_right]
        )

    # EntityMap

    def go_near_entity_map(
        self,
        entities_map: Sequence[EntityMapT],
        use_transport: bool = True,
    ) -> EntityMapT:
        """go nearest entity provided"""

        near_entity = min(
            entities_map,
            key=lambda entity_map: entity_map.map_info.get_dist_map(
                self.get_curr_map_info().map
            ),
        )
        self.travel_to_map(
            [near_entity.map_info],
            use_transport=use_transport,
        )
        return near_entity

    # Buildings

    def go_in_building(self, buildings: Sequence[BuildingInfo]) -> Any:
        near_building = self.go_near_entity_map(buildings)
        res = retry_force_count(CharacterIsStuckException)(near_building.go_in)()
        self.map_state.building = near_building
        self.map_state.curr_direction = FromDirection.UNKNOWN
        return res

    def go_out_building(self) -> Any | None:
        if self.map_state.building is not None:
            res = retry_force_count(CharacterIsStuckException)(
                self.map_state.building.go_out
            )()
            self.map_state.building = None
            self.map_state.curr_direction = FromDirection.UNKNOWN
            return res
        return None

    @overload
    def wait_for_new_map(
        self,
        retry_args: RetryTimeArgs = RetryTimeArgs(),
        is_same_world: bool = True,
        force: Literal[True] = ...,
    ) -> numpy.ndarray: ...

    @overload
    def wait_for_new_map(
        self,
        retry_args: RetryTimeArgs = RetryTimeArgs(),
        is_same_world: bool = True,
        force: Literal[False] = ...,
    ) -> numpy.ndarray | None: ...

    def wait_for_new_map(
        self,
        retry_args: RetryTimeArgs = RetryTimeArgs(offset_start=0, wait_end=(0, 0)),
        is_same_world: bool = True,
        force: bool = False,
    ) -> numpy.ndarray | None:
        img: numpy.ndarray | None = self.animation_manager.wait_animation(
            self.get_curr_map_info().img,
            INFO_MAP_REGION,
            retry_args,
            force,  # type: ignore
        )
        if img is not None:
            is_new_map, img = self.on_new_map()
            if not is_new_map:
                return self.wait_for_new_map(retry_args, is_same_world, force)  # type: ignore
        return img

    def wait_for_new_map_walking(
        self,
        args: WaitForNewMapWalking = WaitForNewMapWalking(),
    ) -> tuple[numpy.ndarray | None, bool]:
        """wait for new map based on character walking, used for going neighbor map for example

        Returns:
            tuple[numpy.ndarray | None, bool]: the new img, was teleported bool
        """
        return self.wait_for_new_map(args.retry_args), False

    def change_map(self) -> numpy.ndarray:
        for map_direction in MapService.get_map_neighbors(
            self.service, self.get_curr_map_info().map.id
        ):
            new_img, _ = self.go_to_neighbor(map_direction, do_trust=False)
            if new_img is None:
                continue
            return new_img
        raise UnknowStateException(self.capturer.capture(), "cant_change_map")

    def __handle_neighbor_new_map(
        self,
        img: numpy.ndarray | None,
        map_direction: MapDirectionSchema,
        was_teleported: bool = False,
        do_trust: bool = True,
    ) -> tuple[numpy.ndarray | None, bool]:
        """Use after clicking and waiting new map result
        Returns:
            tuple[numpy.ndarray | None, bool]: bool is should retry value
        """
        if was_teleported:
            # character was teleported (example : dead after fight), do no retry
            if self.get_curr_map_info().map.waypoint is not None:
                self.map_state.curr_direction = FromDirection.WAYPOINT
            else:
                self.map_state.curr_direction = FromDirection.UNKNOWN
            return None, False

        if img is None:
            # no new map, try again
            return None, True

        if map_direction.from_map_id == self.get_curr_map_info().map.id:
            # new map but same coordinates, try again
            return img, True

        self.map_state.curr_direction = get_inverted_direction(
            map_direction.to_direction
        )
        self.logger.info(f"New curr direction : {self.get_curr_direction()}")
        if map_direction.to_map_id == self.get_curr_map_info().map.id:
            # success
            if do_trust and not map_direction.was_checked:
                MapService.confirm_map_direction(
                    self.service, map_direction.id, map_direction.to_map_id
                )
            return img, False

        # Changed map, but unexpected map
        self.logger.warning(
            f"Map : {self.get_curr_map_info().map} != {map_direction.to_map}"
        )
        if do_trust:
            if not map_direction.was_checked:
                MapService.confirm_map_direction(
                    self.service, map_direction.id, self.get_curr_map_info().map.id
                )
            # else:
            #     raise UnknowStateException(self.image_manager.capture(), "unexpected_map")

        return None, False

    def go_to_neighbor(
        self,
        map_direction: MapDirectionSchema,
        do_trust: bool = True,
        use_shift: bool = False,
        wait_new_map_walking_args=WaitForNewMapWalking(),
    ) -> tuple[numpy.ndarray | None, bool]:
        self.go_out_building()

        was_teleported = False
        pos_direction = get_pos_to_direction(map_direction.to_direction)

        for _ in range(MAX_RETRY):
            with (
                self.controller.hold(win32con.VK_SHIFT) if use_shift else nullcontext()
            ):
                self.controller.click(pos_direction)

            new_img, was_teleported = self.wait_for_new_map_walking(
                wait_new_map_walking_args
            )
            new_img, should_retry = self.__handle_neighbor_new_map(
                new_img, map_direction, was_teleported, do_trust=do_trust
            )
            if not should_retry:
                return new_img, was_teleported

        self.logger.info(
            f"No new map : {self.get_curr_map_info().map} != {map_direction.to_map}"
        )
        if do_trust:
            if not map_direction.was_checked:
                if (
                    len(
                        MapService.get_map_neighbors(
                            self.service,
                            self.get_curr_map_info().map.id,
                            self.get_curr_direction(),
                        )
                    )
                    <= 1
                ):
                    raise UnknowStateException(
                        self.get_curr_map_info().img,
                        f"{self.get_curr_map_info().map} should have atleast one map direction",
                    )
                MapService.delete_map_direction(self.service, map_direction.id)
            else:
                raise UnknowStateException(
                    self.capturer.capture(), "unexpected_no_new_map"
                )

        return None, was_teleported

    def travel_to_world(
        self,
        world_id: int,
        use_transport: bool = True,
        waypoints: list[WaypointSchema] | None = None,
    ) -> numpy.ndarray:
        def dialog_portal_twelve() -> numpy.ndarray | None:
            self.controller.click(PORTAL_TWELVE_TAKE_POSITION)
            wait((0.3, 0.5))
            self.controller.click(PORTAL_TWELVE_ACCEPT_POSITION)
            wait((0.3, 0.5))
            self.controller.click(PORTAL_TWELVE_CONFIRM_POSITION)
            return self.wait_for_new_map(is_same_world=False)

        def enter_portal_to_incar() -> numpy.ndarray | None:
            self.controller.click(PORTAL_INCARNAM_ENTER_POSITION)
            return self.wait_for_new_map()

        def take_portal_to_incar() -> numpy.ndarray | None:
            self.controller.click(PORTAL_INCARNAM_TAKE_POSITION)
            return self.wait_for_new_map(is_same_world=False)

        if self.get_curr_map_info().map.world_id == 2:
            if world_id == 1:
                self.travel_to_map(
                    [
                        get_portal_map_id_by_world()[
                            self.get_curr_map_info().map.world_id, world_id
                        ]
                    ],
                    waypoints,
                    False,  # do not use zaap in incarnam
                )
                img = retry_force_count(CharacterIsStuckException)(
                    dialog_portal_twelve
                )()
                self.map_state.curr_direction = FromDirection.UNKNOWN
                return img
        elif self.get_curr_map_info().map.world_id == 1:
            if world_id == 2:
                self.travel_to_map(
                    [
                        get_portal_map_id_by_world()[
                            self.get_curr_map_info().map.world_id, world_id
                        ],
                    ],
                    waypoints,
                    use_transport,
                )
                retry_count(2)(enter_portal_to_incar)()
                img = retry_force_count(CharacterIsStuckException)(
                    take_portal_to_incar
                )()
                self.map_state.curr_direction = FromDirection.UNKNOWN
                return img

        raise NotImplementedError(
            f"Can't go to {world_id} from {self.get_curr_map_info().map.world_id}"
        )

    def travel_to_map(
        self,
        target_maps: Sequence[BaseMapSchema],
        available_waypoints: list[WaypointSchema] | None = None,
        use_transport: bool = True,
    ) -> numpy.ndarray:
        if available_waypoints is None:
            available_waypoints = CharacterService.get_waypoints(
                self.service, self.character_state.character.id
            )

        self.init_first_move(
            self.get_curr_map_info().img,
            target_maps,
            use_transport,
            available_waypoints,
        )

        if self.get_curr_map_info().map.world_id != target_maps[0].world_id:
            self.travel_to_world(
                target_maps[0].world_id, use_transport, available_waypoints
            )

        path_map = MapService.find_path(
            self.service,
            self.character_state.character.is_sub,
            use_transport,
            self.get_curr_map_info().map.id,
            self.get_curr_direction(),
            [elem.id for elem in available_waypoints],
            [elem.id for elem in target_maps],
        )
        if path_map is None:
            self.logger.info(
                f"Path from {self.get_curr_map_info().map} from direction : {self.get_curr_direction()} to {target_maps} not found..."
            )
            raise CharacterIsStuckException()

        self.logger.info("Found path")
        for action_map_change in path_map:
            if isinstance(action_map_change.from_action, MapDirectionSchema):
                new_img, was_teleported = self.go_to_neighbor(
                    action_map_change.from_action
                )
                if new_img is None or was_teleported:
                    return self.travel_to_map(
                        target_maps, available_waypoints, use_transport
                    )
            elif isinstance(action_map_change.from_action, WaypointSchema):
                self.use_zaap(action_map_change.from_action)
            elif isinstance(action_map_change.from_action, ZaapiSchema):
                self.use_zaapi(action_map_change.from_action)

        if self.map_state.building is not None:
            self.go_out_building()

        return self.get_curr_map_info().img

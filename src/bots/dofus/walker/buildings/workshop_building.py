from logging import Logger
import numpy
from EzreD2Shared.shared.consts.adaptative.positions import (
    WORKSHOP_ALCHEMIST_IN,
    WORKSHOP_ALCHEMIST_OUT,
    WORKSHOP_FISHER_IN,
    WORKSHOP_FISHER_OUT,
    WORKSHOP_PEASANT_IN,
    WORKSHOP_PEASANT_OUT,
    WORKSHOP_WOODCUTTER_IN,
    WORKSHOP_WOODCUTTER_OUT,
)
from EzreD2Shared.shared.consts.object_configs import ObjectConfigs
from EzreD2Shared.shared.entities.position import Position
from EzreD2Shared.shared.enums import JobEnum

from src.bots.dofus.walker.core_walker_system import CoreWalkerSystem
from src.bots.dofus.walker.maps import (
    get_bonta_workshop_alchemist_map,
    get_bonta_workshop_fisher_map,
    get_bonta_workshop_peasant_map,
    get_bonta_workshop_woodcutter_map,
)
from src.common.retry import retry_force_count
from src.entities.building_info import BuildingInfo
from src.exceptions import CharacterIsStuckException
from src.image_manager.screen_objects.image_manager import ImageManager
from src.window_manager.controller import Controller


class WorkshopBuilding:
    def __init__(
        self,
        core_walker_sys: CoreWalkerSystem,
        logger: Logger,
        controller: Controller,
        image_manager: ImageManager,
    ) -> None:
        self.core_walker_sys = core_walker_sys
        self.logger = logger
        self.controller = controller
        self.image_manager = image_manager

    def go_workshop_for_job(self, job_name: str) -> Position:
        match job_name:
            case JobEnum.ALCHIMIST:
                return self.go_to_workshop_alchimist()
            case JobEnum.WOODCUTTER:
                return self.go_to_workshop_woodcutter()
            case JobEnum.FISHERMAN:
                return self.go_to_workshop_fisherman()
            case JobEnum.PEASANT:
                return self.go_to_workshop_peasant()
        raise ValueError(f"No workshop for this job : {job_name}")

    def open_material_workshop(self, pos: Position) -> numpy.ndarray:
        def open() -> numpy.ndarray | None:
            self.logger.info(f"Opening material at {pos}")
            self.controller.click(pos)
            if (
                info := self.image_manager.wait_on_screen(ObjectConfigs.Text.receipe)
            ) is not None:
                return info[2]
            return None

        return retry_force_count(CharacterIsStuckException)(open)()

    @property
    def _workshop_woodcutter(self) -> list[BuildingInfo]:
        return [
            BuildingInfo(
                map_info=get_bonta_workshop_woodcutter_map(),
                go_in=self.__go_in_workshop_woodcutter_bonta,
                go_out=self.__go_out_workshop_woodcutter_bonta,
            )
        ]

    def go_to_workshop_woodcutter(self) -> Position:
        return self.core_walker_sys.go_in_building(self._workshop_woodcutter)

    def __go_in_workshop_woodcutter_bonta(self) -> Position | None:
        self.controller.click(WORKSHOP_WOODCUTTER_IN)
        if (
            info := self.image_manager.wait_on_screen(
                ObjectConfigs.WorkShop.material_woodcutter,
                map_id=self.core_walker_sys.get_curr_map_info().map.id,
            )
        ) is not None:
            return info[0]
        return None

    def __go_out_workshop_woodcutter_bonta(self) -> Position | None:
        self.controller.click(WORKSHOP_WOODCUTTER_OUT)
        if (
            info := self.image_manager.wait_on_screen(
                ObjectConfigs.PathFinding.zaapi,
                map_id=self.core_walker_sys.get_curr_map_info().map.id,
            )
        ) is not None:
            return info[0]
        return None

    @property
    def _workshop_fisherman(self) -> list[BuildingInfo]:
        return [
            BuildingInfo(
                map_info=get_bonta_workshop_fisher_map(),
                go_in=self.__go_in_workshop_fisherman_bonta,
                go_out=self.__go_out_workshop_fisherman_bonta,
            )
        ]

    def go_to_workshop_fisherman(self) -> Position:
        return self.core_walker_sys.go_in_building(self._workshop_fisherman)

    def __go_in_workshop_fisherman_bonta(self) -> Position | None:
        self.controller.click(WORKSHOP_FISHER_IN)
        if (
            info := self.image_manager.wait_on_screen(
                ObjectConfigs.WorkShop.material_fisher,
                map_id=self.core_walker_sys.get_curr_map_info().map.id,
            )
        ) is not None:
            return info[0]
        return None

    def __go_out_workshop_fisherman_bonta(self) -> Position | None:
        self.controller.click(WORKSHOP_FISHER_OUT)
        if (
            info := self.image_manager.wait_on_screen(
                ObjectConfigs.PathFinding.zaapi,
                map_id=self.core_walker_sys.get_curr_map_info().map.id,
            )
        ) is not None:
            return info[0]
        return None

    @property
    def _workshop_peasant(self) -> list[BuildingInfo]:
        return [
            BuildingInfo(
                map_info=get_bonta_workshop_peasant_map(),
                go_in=self.__go_in_workshop_peasant_bonta,
                go_out=self.__go_out_workshop_peasant_bonta,
            )
        ]

    def go_to_workshop_peasant(self) -> Position:
        return self.core_walker_sys.go_in_building(self._workshop_peasant)

    def __go_in_workshop_peasant_bonta(self) -> Position | None:
        self.controller.click(WORKSHOP_PEASANT_IN)
        if (
            info := self.image_manager.wait_on_screen(
                ObjectConfigs.WorkShop.material_peasant,
                map_id=self.core_walker_sys.get_curr_map_info().map.id,
            )
        ) is not None:
            return info[0]
        return None

    def __go_out_workshop_peasant_bonta(self) -> Position | None:
        self.controller.click(WORKSHOP_PEASANT_OUT)
        if (
            info := self.image_manager.wait_on_screen(
                ObjectConfigs.PathFinding.zaapi,
                map_id=self.core_walker_sys.get_curr_map_info().map.id,
            )
        ) is not None:
            return info[0]
        return None

    @property
    def _workshop_alchimist(self) -> list[BuildingInfo]:
        return [
            BuildingInfo(
                map_info=get_bonta_workshop_alchemist_map(),
                go_in=self.__go_in_workshop_alchimist_bonta,
                go_out=self.__go_out_workshop_alchimist_bonta,
            )
        ]

    def go_to_workshop_alchimist(self) -> Position:
        return self.core_walker_sys.go_in_building(self._workshop_alchimist)

    def __go_in_workshop_alchimist_bonta(self) -> Position | None:
        self.controller.click(WORKSHOP_ALCHEMIST_IN)
        if (
            info := self.image_manager.wait_on_screen(
                ObjectConfigs.WorkShop.material_alchimist,
                map_id=self.core_walker_sys.get_curr_map_info().map.id,
            )
        ) is not None:
            return info[0]
        return None

    def __go_out_workshop_alchimist_bonta(self) -> Position | None:
        self.controller.click(WORKSHOP_ALCHEMIST_OUT)
        if (
            info := self.image_manager.wait_on_screen(
                ObjectConfigs.PathFinding.zaapi,
                map_id=self.core_walker_sys.get_curr_map_info().map.id,
            )
        ) is not None:
            return info[0]
        return None

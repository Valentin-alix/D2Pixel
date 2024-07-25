from logging import Logger

from D2Shared.shared.consts.adaptative.positions import (
    BANK_ASTRUB_IN,
    BANK_ASTRUB_OUT,
    BANK_BONTA_IN,
    BANK_BONTA_OUT,
)
from D2Shared.shared.consts.object_configs import ObjectConfigs
from src.bots.dofus.walker.core_walker_system import CoreWalkerSystem
from src.bots.dofus.walker.maps import get_astrub_bank_map, get_bonta_bank_map
from src.entities.building_info import BuildingInfo
from src.image_manager.screen_objects.image_manager import ImageManager
from src.services.client_service import ClientService
from src.window_manager.controller import Controller


class BankBuilding:
    def __init__(
        self,
        core_walker_sys: CoreWalkerSystem,
        logger: Logger,
        controller: Controller,
        image_manager: ImageManager,
        service: ClientService,
    ) -> None:
        self.core_walker_sys = core_walker_sys
        self.logger = logger
        self.controller = controller
        self.image_manager = image_manager
        self.service = service

    @property
    def _banks(self) -> list[BuildingInfo]:
        return [
            BuildingInfo(
                map_info=get_astrub_bank_map(self.service),
                go_in=self.__go_in_bank_astrub,
                go_out=self.__go_out_bank_astrub,
            ),
            BuildingInfo(
                map_info=get_bonta_bank_map(self.service),
                go_in=self.__go_in_bank_bonta,
                go_out=self.__go_out_bank_bonta,
            ),
        ]

    def go_to_bank(self):
        return self.core_walker_sys.go_in_building(self._banks)

    def __go_in_bank_astrub(self):
        self.logger.info("Go in bank astrub")
        self.controller.click(BANK_ASTRUB_IN)
        return self.core_walker_sys.wait_for_new_map()

    def __go_out_bank_astrub(self):
        self.logger.info("Go out bank astrub")
        self.controller.click(BANK_ASTRUB_OUT)
        return self.core_walker_sys.wait_for_new_map()

    def __go_in_bank_bonta(self):
        self.logger.info("Go in bank bonta")
        self.controller.click(BANK_BONTA_IN)
        return self.image_manager.wait_on_screen(ObjectConfigs.Bank.owl_bonta)

    def __go_out_bank_bonta(self):
        self.logger.info("Go out bank bonta")
        self.controller.click(BANK_BONTA_OUT)
        return self.image_manager.wait_on_screen(
            ObjectConfigs.PathFinding.zaapi,
            map_id=self.core_walker_sys.get_curr_map_info().map.id,
        )

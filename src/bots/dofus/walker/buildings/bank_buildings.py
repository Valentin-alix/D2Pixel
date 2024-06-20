from EzreD2Shared.shared.consts.adaptative.positions import (
    BANK_ASTRUB_IN,
    BANK_ASTRUB_OUT,
    BANK_BONTA_IN,
    BANK_BONTA_OUT,
)
from EzreD2Shared.shared.consts.object_configs import ObjectConfigs

from src.bots.dofus.walker.maps import get_astrub_bank_map, get_bonta_bank_map
from src.bots.dofus.walker.walker_system import WalkerSystem
from src.entities.building_info import BuildingInfo


class BankBuilding(WalkerSystem):
    @property
    def _banks(self) -> list[BuildingInfo]:
        return [
            BuildingInfo(
                map_info=get_astrub_bank_map(),
                go_in=self.__go_in_bank_astrub,
                go_out=self.__go_out_bank_astrub,
            ),
            BuildingInfo(
                map_info=get_bonta_bank_map(),
                go_in=self.__go_in_bank_bonta,
                go_out=self.__go_out_bank_bonta,
            ),
        ]

    def go_to_bank(self):
        return self.go_in_building(self._banks)

    def __go_in_bank_astrub(self):
        self.log_info("Go in bank astrub")
        self.click(BANK_ASTRUB_IN)
        return self.wait_for_new_map()

    def __go_out_bank_astrub(self):
        self.log_info("Go out bank astrub")
        self.click(BANK_ASTRUB_OUT)
        return self.wait_for_new_map()

    def __go_in_bank_bonta(self):
        self.log_info("Go in bank bonta")
        self.click(BANK_BONTA_IN)
        return self.wait_on_screen(ObjectConfigs.Bank.owl_bonta)

    def __go_out_bank_bonta(self):
        self.log_info("Go out bank bonta")
        self.click(BANK_BONTA_OUT)
        return self.wait_on_screen(
            ObjectConfigs.PathFinding.zaapi, map_id=self.get_curr_map_info().map.id
        )

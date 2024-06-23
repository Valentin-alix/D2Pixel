import unittest

from src.bots.dofus.sub_area_farming.sub_area_farming_system import (
    SubAreaFarming,
)
from src.bots.modules.fighter.fighter_sub_area_farming import (
    FighterSubAreaFarming,
    get_weights_fight_map,
)
from src.bots.modules.harvester.harvest_sub_area_farming import (
    HarvestSubAreaFarming,
    get_weights_harvest_map,
)
from src.gui.signals.dofus_signals import BotSignals
from src.window_manager.organizer import WindowInfo


class TestWeightSubArea(unittest.TestCase):
    def setUp(self) -> None:
        self.sub_area_farming = SubAreaFarming(
            window_info=WindowInfo(hwnd=1, name="temp"), bot_signals=BotSignals()
        )
        self.sub_area_fighter_farming = FighterSubAreaFarming(
            fighter_maps_time={}, fighter_sub_areas_farming_ids=[], character_id="temp"
        )
        self.harvest_sub_area_farm = HarvestSubAreaFarming(
            window_info=WindowInfo(hwnd=1, name="temp"),
            harvest_sub_areas_farming_ids=[],
            harvest_map_time={},
            bot_signals=BotSignals(),
        )

        return super().setUp()

    def test_weight_map_fight(self):
        self.sub_area_farming.character.lvl = 100
        valid_sub_areas = (
            SessionLocal.query(SubArea)
            .filter(SubArea.level <= self.sub_area_farming.character.lvl)
            .all()
        )
        weights = get_weights_fight_map(SessionLocal(), 1, valid_sub_areas, 5)

        weights = get_weights_harvest_map(
            SessionLocal(),
            1,
            self.sub_area_farming.character.get_possible_collectable(SessionLocal()),
            valid_sub_areas,
        )
        weights = dict(
            sorted(weights.items(), key=lambda elem: elem[1], reverse=True)[:200]
        )
        for map, weight in weights.items():
            print(map, weight)
        # print(weights)

    def test_get_valid_fighter(self):
        self.sub_area_fighter_farming.character.lvl = 100

        SessionLocal.commit()
        valid = self.sub_area_fighter_farming.get_valid_sub_areas_fighter()

        weights = get_weights_fight_map(SessionLocal(), 1, valid, 100)
        ans = self.sub_area_farming.get_average_sub_area_weight(valid[0], weights)
        print(ans)

        max_time = self.sub_area_fighter_farming.get_max_time_fighter(valid)
        print(max_time)

    def test_harvest(self):
        temp = self.harvest_sub_area_farm.get_valid_sub_areas_harvester()
        self.harvest_sub_area_farm.get_max_time_harvester(temp)
        print(temp)

        sub_area_ids = [elem.id for elem in temp]

        ToMapAlias = aliased(Map)
        limit_maps = (
            SessionLocal.query(Map)
            .join(SubArea, SubArea.id == Map.sub_area_id)
            .filter(SubArea.id.in_(sub_area_ids))
            .join(MapDirection, MapDirection.from_map_id == Map.id)
            .join(ToMapAlias, ToMapAlias.id == MapDirection.to_map_id)
            .filter(
                or_(
                    ToMapAlias.sub_area_id.not_in(sub_area_ids),
                    and_(Map.waypoint != None, Map.world_id != 2),
                )
            )
            .all()
        )
        print(limit_maps)

import unittest
from time import perf_counter

from src.bots.dofus.walker.astar_maps import AstarMap
from src.data_layer.database import SessionLocal
from src.data_layer.models.map_direction import FromDirection
from src.data_layer.queries.map import get_related_map
from src.data_layer.schemas.map import MapSchema


class TestAstar(unittest.TestCase):
    def test_astar_map(self):
        session = SessionLocal()

        # all_maps = (
        #     session.query(Map)
        #     .join(SubArea, SubArea.id == Map.sub_area_id)
        #     .filter(Map.world_id == 1, SubArea.area_id == 7)
        #     .all()
        # )
        # draw_maps_on_grid(all_maps)

        start_map = get_related_map(
            session, MapSchema(x=1, y=0, world_id=1), force=True
        )

        end_maps = [
            get_related_map(session, MapSchema(x=10, y=-3, world_id=1), force=True)
        ]

        waypoints = start_map.sub_area.world.get_waypoints(session)

        before = perf_counter()

        astar_map = AstarMap(True, True, waypoints, session)
        path = astar_map.find_path(start_map, FromDirection.BOT, end_maps)

        print(list(path))

        print(perf_counter() - before)

        # print(path_map)

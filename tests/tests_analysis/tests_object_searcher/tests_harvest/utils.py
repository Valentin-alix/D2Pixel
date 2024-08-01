import os
from collections import defaultdict
from logging import Logger
from pathlib import Path

import cv2
import numpy
from tqdm import tqdm

from D2Shared.shared.consts.object_configs import COLLECTABLE_CONFIG_BY_NAME
from D2Shared.shared.entities.object_search_config import ObjectSearchConfig
from D2Shared.shared.entities.position import Position
from D2Shared.shared.schemas.map import CoordinatesMapSchema, MapSchema
from D2Shared.shared.schemas.region import RegionSchema
from src.gui.signals.app_signals import AppSignals
from src.image_manager.debug import (
    ColorBGR,
    draw_area,
    draw_position,
    draw_text,
)
from src.image_manager.screen_objects.object_searcher import (
    ObjectSearcher,
)
from src.services.map import MapService
from src.services.session import ServiceSession

PATH_FIXTURES = os.path.join(
    Path(__file__).parent.parent.parent.parent, "fixtures", "maps"
)


def get_collectables_with_refs(
    img: numpy.ndarray,
    config: ObjectSearchConfig,
    ref_utilities: dict[str, int],
    map_id: int,
    object_searcher: ObjectSearcher,
) -> tuple[list[Position], dict[str, int]]:
    positions: list[Position] = []

    for pos, template_found_place in object_searcher.get_multiple_position(
        img, config, map_id=map_id
    ):
        ref_utilities[template_found_place.filename] += 1
        positions.append(pos)

    return positions, ref_utilities


def draw_errors_img(
    img: numpy.ndarray,
    found_positions: list[Position],
    info_res: list[RegionSchema] | int,
):
    for pos in found_positions:
        draw_position(img, pos)

    if isinstance(info_res, int):
        draw_text(img, info_res)
    else:
        for area in info_res:
            draw_area(img, area, ColorBGR.RED)


def parse_line_position(line: str) -> tuple[str, list[RegionSchema]]:
    filename = line.split(" ")[0]
    count_res = line.split(" ")[1]
    areas: list[RegionSchema] = []
    for index in range(int(count_res)):
        x = int(line.split(" ")[2 + 4 * index])
        y = int(line.split(" ")[3 + 4 * index])
        w = int(line.split(" ")[4 + 4 * index])
        h = int(line.split(" ")[5 + 4 * index])
        areas.append(RegionSchema(left=x, top=y, right=x + w, bot=y + h))

    return filename, areas


def get_errors_resource(
    resource_names: list[str], debug: bool = False
) -> tuple[int, list[numpy.ndarray], list[numpy.ndarray], dict[str, int]]:
    logger = Logger("root")
    service = ServiceSession(logger, AppSignals())
    object_searcher = ObjectSearcher(logger=logger, service=service)

    def get_related_filename(map: tuple[int, int]) -> str | None:
        return next(
            (
                elem
                for elem in os.listdir(PATH_FIXTURES)
                if elem[:-4] == "_".join((str(elem) for elem in map))
            ),
            None,
        )

    def get_related_map_filename(filename: str) -> MapSchema:
        x, y = filename[:-4].split("_")
        return MapService.get_related_map(
            service, CoordinatesMapSchema(x=int(x), y=int(y), world_id=1)
        )

    config = COLLECTABLE_CONFIG_BY_NAME[resource_names[0]]
    tests_maps_infos: dict[str, int] = defaultdict(lambda: 0)

    total = len(tests_maps_infos.keys())

    not_founds: list[numpy.ndarray] = []
    false_positives: list[numpy.ndarray] = []

    ref_utilities: dict[str, int] = defaultdict(lambda: 0)

    for filename, count in tqdm(tests_maps_infos.items(), total=total):
        map = get_related_map_filename(filename)
        # TODO Collectable service get expected res count
        img = cv2.imread(os.path.join(PATH_FIXTURES, filename))

        positions, ref_utilities = get_collectables_with_refs(
            img, config, ref_utilities, map.id, object_searcher
        )
        if count > len(positions):
            draw_errors_img(img, positions, count)
            not_founds.append(img)

    if debug:
        for not_found in not_founds:
            cv2.imshow("not found", not_found)
            if cv2.waitKey() == ord("q"):
                break
        for false_positive in false_positives:
            cv2.imshow("false positive", false_positive)
            if cv2.waitKey() == ord("q"):
                break

    print(ref_utilities.items())
    print(len(not_founds), len(false_positives))

    return (total, not_founds, false_positives, ref_utilities)

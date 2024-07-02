import math
import os
from typing import Iterator, Literal, Sequence, overload

from cachetools import cached
from cachetools.keys import hashkey
import cv2
import numpy
from D2Shared.shared.entities.object_search_config import ObjectSearchConfig
from D2Shared.shared.entities.position import Position
from D2Shared.shared.schemas.region import RegionSchema
from D2Shared.shared.schemas.template_found import (
    InfoTemplateFoundPlacementSchema,
    TemplateFoundPlacementSchema,
)

from src.consts import ASSET_FOLDER_PATH
from src.exceptions import UnknowStateException
from src.image_manager.analysis import (
    iter_position_template_in_image,
)
from src.image_manager.transformation import (
    crop_image,
    img_to_gray,
    img_to_hsv,
)
from src.services.session import ServiceSession
from src.services.template import TemplateService

TEMPLATE_FOLDER = os.path.join(ASSET_FOLDER_PATH, "templates")


@cached(cache={}, key=lambda config: hashkey(config))
def get_templates(config: ObjectSearchConfig) -> dict[str, numpy.ndarray]:
    templates_by_filename: dict[str, numpy.ndarray] = {}
    for folder, _, files in os.walk(TEMPLATE_FOLDER):
        key_folder = ".".join(
            (_elem for _elem in folder.split("templates")[1].split("\\") if _elem != "")
        )
        if key_folder != "":
            key_folder += "."
        for file in files:
            template_name = f"{key_folder}{file[:-4]}"
            if template_name.startswith(config.ref):
                path_template = os.path.join(folder, file)
                templates_by_filename[file[:-4]] = get_prepared_img(
                    cv2.imread(path_template), config, with_crop=False
                )
    return templates_by_filename


def get_prepared_img(
    img: numpy.ndarray, config: ObjectSearchConfig, with_crop: bool = True
) -> numpy.ndarray:
    if config.lookup_region is not None and with_crop:
        img = crop_image(img, config.lookup_region)
    if config.grey_scale:
        img = img_to_gray(img)
    else:
        img = img_to_hsv(img)
    return img


def get_region_from_template(template: numpy.ndarray, pos: Position) -> RegionSchema:
    height, width = template.shape[:2]
    return RegionSchema(
        left=max(math.floor(pos.x_pos - (width / 2)), 0),
        right=math.ceil(pos.x_pos + (width / 2)),
        top=max(math.floor(pos.y_pos - (height / 2)), 0),
        bot=math.ceil(pos.y_pos + (height / 2)),
    )


class ObjectSearcher:
    def __init__(self, service: ServiceSession) -> None:
        self.service = service

    def iter_position_from_template_info(
        self,
        img: numpy.ndarray,
        object_config: ObjectSearchConfig,
        templates_found_placement: Sequence[InfoTemplateFoundPlacementSchema],
    ) -> Iterator[tuple[Position, InfoTemplateFoundPlacementSchema]]:
        img = get_prepared_img(img, object_config, with_crop=False)

        for template_found_placement in templates_found_placement:
            _img = crop_image(img, template_found_placement.region)
            related_template = get_templates(object_config)[
                template_found_placement.filename
            ]
            for position in iter_position_template_in_image(
                _img,
                related_template,
                threshold=object_config.threshold,
                offset_area=template_found_placement.region,
            ):
                yield (position, template_found_placement)

    def iter_position(
        self,
        img: numpy.ndarray,
        config: ObjectSearchConfig,
        map_id: int | None = None,
        use_cache: bool = True,
    ) -> Iterator[tuple[Position, InfoTemplateFoundPlacementSchema]]:
        if (
            config.cache_info is not None
            and (
                templates_place := TemplateService.get_template_from_config(
                    self.service, config, map_id
                )
            )
            is not None
            and use_cache
        ):
            for (
                position,
                template_found_place,
            ) in self.iter_position_from_template_info(img, config, templates_place):
                yield position, template_found_place
        else:
            img = get_prepared_img(img, config, use_cache)
            for filename, template in get_templates(config).items():
                for position in iter_position_template_in_image(
                    img,
                    template,
                    threshold=config.threshold,
                    offset_area=config.lookup_region if use_cache else None,
                ):
                    region_schema = get_region_from_template(template, position)
                    yield (
                        position,
                        InfoTemplateFoundPlacementSchema(
                            filename=filename, region=region_schema
                        ),
                    )

    @overload
    def get_position(
        self,
        img: numpy.ndarray,
        config: ObjectSearchConfig,
        map_id: int | None = None,
        force: Literal[False] = ...,
        use_cache: bool = True,
    ) -> tuple[Position, TemplateFoundPlacementSchema] | None: ...

    @overload
    def get_position(
        self,
        img: numpy.ndarray,
        config: ObjectSearchConfig,
        map_id: int | None = None,
        force: Literal[True] = ...,
        use_cache: bool = True,
    ) -> tuple[Position, TemplateFoundPlacementSchema]: ...

    def get_position(
        self,
        img: numpy.ndarray,
        config: ObjectSearchConfig,
        map_id: int | None = None,
        force: bool = False,
        use_cache: bool = True,
    ) -> tuple[Position, InfoTemplateFoundPlacementSchema] | None:
        pos_info = next((self.iter_position(img, config, map_id, use_cache)), None)
        if force and not pos_info:
            raise UnknowStateException(img, config.ref.replace(".", "_"))

        if pos_info is not None:
            pos, template_found_info = pos_info
            if (
                config.cache_info is not None
                and config.cache_info.min_parsed_count_on_map is not None
                and use_cache
            ):
                template_found_place = TemplateService.get_place_or_create(
                    self.service,
                    config=config,
                    filename=template_found_info.filename,
                    region_schema=template_found_info.region,
                    map_id=map_id,
                )
                if template_found_place.template_found_map_id is not None:
                    TemplateService.increment_count_template_map(
                        self.service, template_found_place.template_found_map_id
                    )
            return pos, template_found_info
        return None

    def get_multiple_position(
        self,
        img: numpy.ndarray,
        config: ObjectSearchConfig,
        map_id: int | None = None,
        use_cache: bool = True,
    ) -> list[tuple[Position, InfoTemplateFoundPlacementSchema]]:
        pos_infos = list(self.iter_position(img, config, map_id, use_cache))
        if config.cache_info and config.cache_info.min_parsed_count_on_map is not None:
            incremented_template_found_map_ids: set[int] = set()
            for _, template_found_info in pos_infos:
                template_found_place = TemplateService.get_place_or_create(
                    self.service,
                    config=config,
                    filename=template_found_info.filename,
                    region_schema=template_found_info.region,
                    map_id=map_id,
                )
                if (
                    template_found_place.template_found_map_id
                    in incremented_template_found_map_ids
                    or template_found_place.template_found_map_id is None
                ):
                    continue
                TemplateService.increment_count_template_map(
                    self.service, template_found_place.template_found_map_id
                )

        return [(pos_info[0], pos_info[1]) for pos_info in pos_infos]

    def is_not_on_screen(
        self, img: numpy.ndarray, config: ObjectSearchConfig, map_id: int | None = None
    ) -> numpy.ndarray | None:
        if self.get_position(img, config, map_id) is None:
            return img
        return None

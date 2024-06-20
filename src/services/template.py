import requests
from cachetools import TTLCache, cached
from EzreD2Shared.shared.entities.object_search_config import ObjectSearchConfig
from EzreD2Shared.shared.schemas.region import RegionSchema
from EzreD2Shared.shared.schemas.template_found import (
    TemplateFoundPlacementSchema,
)

from src.consts import BACKEND_URL

TEMPLATE_URL = BACKEND_URL + "/template/"


class TemplateService:
    @staticmethod
    @cached(cache=TTLCache(maxsize=256, ttl=300))
    def get_template_from_config(
        config: ObjectSearchConfig, map_id: int | None = None
    ) -> list[TemplateFoundPlacementSchema] | None:
        resp = requests.get(
            f"{TEMPLATE_URL}places/from_config/",
            params={"map_id": map_id},
            json=config.model_dump(),
        )
        if resp.json() is None:
            return None
        return [TemplateFoundPlacementSchema(**elem) for elem in resp.json()]

    @staticmethod
    def increment_count_template_map(
        template_found_map_id: int,
    ):
        requests.put(
            f"{TEMPLATE_URL}template_found_map/{template_found_map_id}/increment_parsed_count"
        )

    @staticmethod
    def get_place_or_create(
        config: ObjectSearchConfig,
        filename: str,
        region_schema: RegionSchema,
        map_id: int | None = None,
    ) -> TemplateFoundPlacementSchema:
        resp = requests.get(
            f"{TEMPLATE_URL}places/or_create",
            params={
                "filename": filename,
                "map_id": map_id,
            },
            json={
                "config": config.model_dump(),
                "region_schema": region_schema.model_dump(),
            },
        )
        return TemplateFoundPlacementSchema(**resp.json())

from cachetools import TTLCache, cached

from D2Shared.shared.entities.object_search_config import ObjectSearchConfig
from D2Shared.shared.schemas.region import RegionSchema
from D2Shared.shared.schemas.template_found import (
    TemplateFoundPlacementSchema,
)
from src.consts import BACKEND_URL
from src.services.client_service import ClientService

TEMPLATE_URL = BACKEND_URL + "/template/"


class TemplateService:
    @staticmethod
    @cached(cache=TTLCache(maxsize=256, ttl=300))
    async def get_template_from_config(
        service: ClientService, config: ObjectSearchConfig, map_id: int | None = None
    ) -> list[TemplateFoundPlacementSchema] | None:
        resp = await service.session.post(
            f"{TEMPLATE_URL}places/from_config/",
            params={"map_id": map_id},
            json=config.model_dump(),
        )
        if resp.json() is None:
            return None
        return [TemplateFoundPlacementSchema(**elem) for elem in resp.json()]

    @staticmethod
    async def increment_count_template_map(
        service: ClientService,
        template_found_map_id: int,
    ):
        await service.session.put(
            f"{TEMPLATE_URL}template_found_map/{template_found_map_id}/increment_parsed_count"
        )

    @staticmethod
    async def get_place_or_create(
        service: ClientService,
        config: ObjectSearchConfig,
        filename: str,
        region_schema: RegionSchema,
        map_id: int | None = None,
    ) -> TemplateFoundPlacementSchema:
        resp = await service.session.post(
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

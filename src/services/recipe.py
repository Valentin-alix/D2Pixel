from cachetools import TTLCache, cached
from cachetools.keys import hashkey

from D2Shared.shared.enums import CategoryEnum
from D2Shared.shared.schemas.recipe import RecipeSchema
from src.consts import BACKEND_URL
from src.services.client_service import ClientService

RECIPE_URL = BACKEND_URL + "/recipe/"


class RecipeService:
    @staticmethod
    async def get_valid_ordered(
        service: ClientService,
        recipe_ids: list[int],
        character_id: str,
    ) -> list[RecipeSchema]:
        resp = await service.session.post(
            f"{RECIPE_URL}valid_ordered/",
            params={"character_id": character_id},
            json=recipe_ids,
        )
        return [RecipeSchema(**elem) for elem in resp.json()]

    @staticmethod
    async def get_available_recipes(
        service: ClientService,
        character_id: str,
    ) -> list[RecipeSchema]:
        resp = await service.session.post(
            f"{RECIPE_URL}available/",
            params={"character_id": character_id},
        )
        return [RecipeSchema(**elem) for elem in resp.json()]

    @staticmethod
    @cached(
        cache=TTLCache(maxsize=100, ttl=600),
        key=lambda _, server_id, category, type_item_id, limit: hashkey(
            server_id, category, type_item_id, limit
        ),
    )
    async def get_best_recipe_benefits(
        service: ClientService,
        server_id: int,
        category: CategoryEnum | None = None,
        type_item_id: int | None = None,
        limit: int = 100,
    ) -> list[tuple[str, float]]:
        resp = await service.session.get(
            f"{RECIPE_URL}best_recipe_benefits/",
            params={
                "server_id": server_id,
                "type_item_id": type_item_id,
                "limit": limit,
                "category": category,
            },
        )
        return resp.json()

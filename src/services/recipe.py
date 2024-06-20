import requests
from EzreD2Shared.shared.enums import CategoryEnum
from EzreD2Shared.shared.schemas.recipe import RecipeSchema

from src.consts import BACKEND_URL

RECIPE_URL = BACKEND_URL + "/recipe/"


class RecipeService:
    @staticmethod
    def get_default_recipes(
        character_id: str,
    ) -> list[RecipeSchema]:
        resp = requests.get(
            f"{RECIPE_URL}craft_default",
            params={"character_id": character_id},
        )
        return [RecipeSchema(**elem) for elem in resp.json()]

    @staticmethod
    def get_best_recipe_benefits(
        server_id: int,
        category: CategoryEnum | None = None,
        type_item_id: int | None = None,
        limit: int = 100,
    ) -> list[tuple[str, float]]:
        resp = requests.get(
            f"{RECIPE_URL}best_recipe_benefits/",
            params={
                "server_id": server_id,
                "type_item_id": type_item_id,
                "limit": limit,
                "category": category,
            },
        )
        return resp.json()

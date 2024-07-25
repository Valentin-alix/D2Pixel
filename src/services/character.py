from D2Shared.shared.schemas.character import (
    CharacterJobInfoSchema,
    CharacterSchema,
    UpdateCharacterSchema,
)
from D2Shared.shared.schemas.collectable import CollectableSchema
from D2Shared.shared.schemas.spell import SpellSchema, UpdateSpellSchema
from src.consts import BACKEND_URL
from src.services.client_service import ClientService

CHARACTER_URL = BACKEND_URL + "/character/"


class CharacterService:
    @staticmethod
    async def update_character(
        service: ClientService, character: UpdateCharacterSchema
    ) -> CharacterSchema:
        resp = await service.session.put(
            f"{CHARACTER_URL}{character.id}", json=character.model_dump()
        )
        return CharacterSchema(**resp.json())

    @staticmethod
    async def update_job_infos(
        service: ClientService,
        character_id: str,
        job_infos: list[CharacterJobInfoSchema],
    ):
        await service.session.put(
            f"{CHARACTER_URL}{character_id}/job_infos",
            json=[elem.model_dump() for elem in job_infos],
        )

    @staticmethod
    async def update_waypoints(
        service: ClientService,
        character_id: str,
        waypoint_ids: list[int],
    ):
        await service.session.put(
            f"{CHARACTER_URL}{character_id}/waypoints",
            params={"character_id": character_id},
            json=waypoint_ids,
        )

    @staticmethod
    async def update_recipes(
        service: ClientService,
        character_id: str,
        recipe_ids: list[int],
    ):
        await service.session.put(
            f"{CHARACTER_URL}{character_id}/recipes",
            params={"character_id": character_id},
            json=recipe_ids,
        )

    @staticmethod
    async def update_spells(
        service: ClientService,
        character_id: str,
        spells: list[UpdateSpellSchema],
    ) -> list[SpellSchema]:
        resp = await service.session.put(
            f"{CHARACTER_URL}{character_id}/spells/",
            json=[elem.model_dump() for elem in spells],
        )
        return [SpellSchema(**elem) for elem in resp.json()]

    @staticmethod
    async def update_sub_areas(
        service: ClientService,
        character_id: str,
        sub_area_ids: list[int],
    ):
        await service.session.put(
            f"{CHARACTER_URL}{character_id}/sub_areas",
            params={"character_id": character_id},
            json=sub_area_ids,
        )

    @staticmethod
    async def add_bank_items(
        service: ClientService,
        character_id: str,
        item_ids: list[int],
    ):
        await service.session.post(
            f"{CHARACTER_URL}{character_id}/bank_items",
            json=item_ids,
        )

    @staticmethod
    async def remove_bank_items(
        service: ClientService,
        character_id: str,
        item_ids: list[int],
    ):
        await service.session.post(
            f"{CHARACTER_URL}{character_id}/bank_items",
            json=item_ids,
        )

    @staticmethod
    async def get_possible_collectable(
        service: ClientService,
        character_id: str,
    ) -> list[CollectableSchema]:
        resp = await service.session.get(
            f"{CHARACTER_URL}{character_id}/possible_collectable"
        )
        return [CollectableSchema(**elem) for elem in resp.json()]

    @staticmethod
    async def get_or_create_character(
        service: ClientService, character_id: str
    ) -> CharacterSchema:
        resp = await service.session.get(f"{CHARACTER_URL}{character_id}/or_create/")
        return CharacterSchema(**resp.json())

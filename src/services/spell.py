from functools import cache

import requests
from EzreD2Shared.shared.enums import CharacteristicEnum, ElemEnum
from EzreD2Shared.shared.schemas.character import CharacterSchema
from EzreD2Shared.shared.schemas.spell_lvl import CurrentBoostSchema, SpellLevelSchema

from src.consts import BACKEND_URL

SPELL_URL = BACKEND_URL + "/spell/"


class SpellService:
    @staticmethod
    @cache
    def get_spell_lvls(character_lvl: int, breed_id: int) -> list[SpellLevelSchema]:
        resp = requests.get(
            f"{SPELL_URL}spell_lvl/",
            params={"character_lvl": character_lvl, "breed_id": breed_id},
        )
        return [SpellLevelSchema(**spell_lvl) for spell_lvl in resp.json()]

    @staticmethod
    @cache
    def get_spell_lvl_for_boost(
        character_lvl: int, breed_id: int, characteristic: CharacteristicEnum
    ) -> SpellLevelSchema | None:
        resp = requests.get(
            f"{SPELL_URL}spell_lvl/for_boost/",
            params={
                "character_lvl": character_lvl,
                "breed_id": breed_id,
                "characteristic": characteristic,
            },
        )
        if resp.json() is None:
            return None
        return SpellLevelSchema(**resp.json())

    @staticmethod
    @cache
    def check_if_boost_for_characteristic(
        spell_lvl: SpellLevelSchema, characteristic: CharacteristicEnum
    ) -> bool:
        resp = requests.get(
            f"{SPELL_URL}spell_lvl/{spell_lvl.id}/is_boost_for_char/",
            params={"characteristic": characteristic},
        )
        return bool(resp.json())

    @staticmethod
    def get_max_range_valuable_dmg_spell(
        prefered_elem: ElemEnum, po_bonus: int, spell_lvl_ids: list[int]
    ) -> int:
        resp = requests.get(
            f"{SPELL_URL}spell_lvl/max_range_valuable_dmg_spell/",
            params={
                "prefered_elem": prefered_elem,
                "po_bonus": po_bonus,
            },
            json=spell_lvl_ids,
        )
        return int(resp.json())

    @staticmethod
    def get_best_combination(
        dist_from_enemy: float | None,
        spell_lvls_ids: list[int],
        useful_boost_chars: list[CharacteristicEnum],
        use_heal: bool,
        character: CharacterSchema,
        pa: int,
        spell_used_ids_with_count: dict[int, int],
        current_boosts: list[CurrentBoostSchema],
    ) -> list[SpellLevelSchema]:
        resp = requests.get(
            f"{SPELL_URL}spell_lvl/best_combination/",
            params={
                "dist_from_enemy": dist_from_enemy,
                "use_heal": use_heal,
                "pa": pa,
            },
            json={
                "spell_lvls_ids": spell_lvls_ids,
                "useful_boost_chars": useful_boost_chars,
                "character": character.model_dump(),
                "spell_used_ids_with_count": spell_used_ids_with_count,
                "current_boosts": [elem.model_dump() for elem in current_boosts],
            },
        )
        return [SpellLevelSchema(**spell_lvl) for spell_lvl in resp.json()]

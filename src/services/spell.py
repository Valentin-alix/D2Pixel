from D2Shared.shared.enums import CharacteristicEnum
from D2Shared.shared.schemas.spell import (
    CurrentBoostSchema,
    SpellSchema,
)
from src.consts import BACKEND_URL
from src.services.session import ServiceSession

SPELL_URL = BACKEND_URL + "/spell/"


class SpellService:
    @staticmethod
    def get_best_combination(
        service: ServiceSession,
        dist_from_enemy: float | None,
        spell_ids: list[int],
        useful_boost_chars: list[CharacteristicEnum],
        use_heal: bool,
        character_id: str,
        pa: int,
        spell_used_ids_with_count: dict[int, int],
        current_boosts: list[CurrentBoostSchema],
    ) -> list[SpellSchema]:
        with service.logged_session() as session:
            resp = session.get(
                f"{SPELL_URL}best_combination/",
                params={
                    "dist_from_enemy": dist_from_enemy,
                    "use_heal": use_heal,
                    "pa": pa,
                    "character_id": character_id,
                },
                json={
                    "spell_ids": spell_ids,
                    "useful_boost_chars": useful_boost_chars,
                    "spell_used_ids_with_count": spell_used_ids_with_count,
                    "current_boosts": [elem.model_dump() for elem in current_boosts],
                },
            )
            return [SpellSchema(**spell_lvl) for spell_lvl in resp.json()]

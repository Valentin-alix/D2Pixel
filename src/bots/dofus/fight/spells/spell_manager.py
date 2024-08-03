from collections import defaultdict
from dataclasses import dataclass, field

from D2Shared.shared.enums import CharacteristicEnum
from D2Shared.shared.schemas.spell import CurrentBoostSchema, SpellSchema
from src.bots.dofus.fight.grid.grid import Grid
from src.services.session import ServiceSession
from src.states.character_state import CharacterState


@dataclass
class SpellManager:
    grid: Grid
    service: ServiceSession
    character_state: CharacterState

    _pa: int = field(default=6, init=False)
    _turn: int = field(default=0, init=False)
    _spell_used_ids_with_count: dict[int, int] = field(
        default_factory=lambda: defaultdict(lambda: 0), init=False
    )
    _current_boosts: set[CurrentBoostSchema] = field(default_factory=set, init=False)
    _max_range_spell: int | None = field(default=None, init=False)

    def on_start_fight_spells(self):
        self._max_range_spell = self.get_max_range_valuable_dmg_spell()
        self._turn = 0
        self._current_boosts.clear()
        self._spell_used_ids_with_count.clear()

    def on_new_turn_spells(self):
        self._turn += 1
        self._current_boosts = set(
            curr_buff
            for curr_buff in self._current_boosts
            if curr_buff.expire_turn > self._turn
        )
        self._spell_used_ids_with_count.clear()

    def get_range_spell(self, spell: SpellSchema):
        if spell.boostable_range:
            return self.character_state.character.po_bonus + spell.range
        return spell.range

    def get_max_range_valuable_dmg_spell(self) -> int:
        """get max range of dmg spell (prefer same elem)"""
        character = self.character_state.character

        max_range_prefered_spell = sorted(
            (
                _elem
                for _elem in character.spells
                if _elem.level <= self.character_state.character.lvl
            ),
            key=lambda _spell: (
                _spell.elem == character.elem,
                self.get_range_spell(_spell),
            ),
            reverse=True,
        )[0]

        return self.get_range_spell(max_range_prefered_spell)

    def get_spell_lvl_for_boost(self, char: CharacteristicEnum) -> SpellSchema | None:
        character = self.character_state.character
        return next(
            (
                _spell
                for _spell in character.spells
                if _spell.level <= character.lvl and _spell.boost_char == char
            ),
            None,
        )

from collections import defaultdict

from EzreD2Shared.shared.schemas.spell_lvl import CurrentBoostSchema

from src.bots.dofus.fight.grid.grid import Grid
from src.services.spell import SpellService


class SpellManager(Grid):
    _pa: int = 6
    _spell_used_ids_with_count: dict[int, int]
    _current_boosts: set[CurrentBoostSchema]
    _turn: int = 0
    _max_range_spell: int

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._spell_used_ids_with_count = defaultdict(lambda: 0)
        self._current_boosts = set()

    def on_start_fight_spells(self):
        self._max_range_spell = SpellService.get_max_range_valuable_dmg_spell(
            self.character.elem,
            self.character.po_bonus,
            [
                elem.id
                for elem in SpellService.get_spell_lvls(
                    self.character.lvl, self.character.breed_id
                )
            ],
        )
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

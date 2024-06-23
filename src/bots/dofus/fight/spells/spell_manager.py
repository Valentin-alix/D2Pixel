from collections import defaultdict


from EzreD2Shared.shared.schemas.spell_lvl import CurrentBoostSchema
from src.bots.dofus.fight.grid.grid import Grid
from src.services.session import ServiceSession
from src.services.spell import SpellService
from src.states.character_state import CharacterState


class SpellManager:
    _max_range_spell: int

    def __init__(
        self, grid: Grid, service: ServiceSession, character_state: CharacterState
    ) -> None:
        self.grid = grid
        self._pa: int = 6
        self._turn: int = 0
        self._spell_used_ids_with_count: dict[int, int] = defaultdict(lambda: 0)
        self._current_boosts: set[CurrentBoostSchema] = set()
        self.service = service
        self.character_state = character_state

    def on_start_fight_spells(self):
        self._max_range_spell = SpellService.get_max_range_valuable_dmg_spell(
            self.service,
            self.character_state.character.elem,
            self.character_state.character.po_bonus,
            [
                elem.id
                for elem in SpellService.get_spell_lvls(
                    self.service,
                    self.character_state.character.lvl,
                    self.character_state.character.breed_id,
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

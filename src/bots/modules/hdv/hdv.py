from dataclasses import dataclass
from logging import Logger

from D2Shared.shared.schemas.item import SellItemInfo
from src.bots.modules.hdv.craft import Crafter
from src.bots.modules.hdv.sell import Seller
from src.services.recipe import RecipeService
from src.services.session import ServiceSession
from src.states.character_state import CharacterState


@dataclass
class Hdv:
    service: ServiceSession
    character_state: CharacterState
    crafter: Crafter
    seller: Seller
    logger: Logger

    def run(self):
        character = self.character_state.character
        if character.lvl < 10:
            return

        recipes = self.character_state.character.recipes

        recipes = RecipeService.get_valid_ordered(
            self.service,
            [elem.id for elem in recipes],
            self.character_state.character.id,
        )
        if len(recipes) > 0:
            self.logger.info(f"Gonna craft : {recipes}")
            self.crafter.run_crafter(recipes)

        sell_items: list[SellItemInfo] = [
            _elem
            for _elem in self.character_state.character.sell_items_infos
            if _elem.item in self.character_state.character.bank_items
        ]
        if len(sell_items) > 0:
            self.logger.info(f"Gonna sell : {sell_items}")
            self.seller.run_seller(sell_items)

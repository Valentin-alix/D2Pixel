from dataclasses import dataclass
from logging import Logger

from src.bots.modules.hdv.craft import Crafter
from src.bots.modules.hdv.sell import Seller
from src.services.item import ItemService
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

        if len(self.character_state.character.sell_items) == 0:
            # do not sell items that are in ingredient of craft items
            sell_items = ItemService.get_default_sellable_items(
                self.service,
                self.character_state.character.id,
                [_elem.id for _elem in recipes],
            )
        else:
            sell_items = self.character_state.character.sell_items

        if len(sell_items) > 0:
            self.logger.info(f"Gonna sell : {sell_items}")
            self.seller.run_seller(sell_items)

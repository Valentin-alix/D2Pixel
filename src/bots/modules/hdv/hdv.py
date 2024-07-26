from logging import Logger

from D2Shared.shared.schemas.recipe import RecipeSchema
from src.bots.modules.hdv.craft.craft import Crafter
from src.bots.modules.hdv.sell import Seller
from src.services.item import ItemService
from src.services.recipe import RecipeService
from src.services.session import ServiceSession
from src.states.character_state import CharacterState


class Hdv:
    def __init__(
        self,
        service: ServiceSession,
        character_state: CharacterState,
        crafter: Crafter,
        seller: Seller,
        logger: Logger,
    ) -> None:
        self.logger = logger
        self.service = service
        self.character_state = character_state

        self.crafter = crafter
        self.seller = seller

    def run(self, recipes: list[RecipeSchema] | None = None):
        character = self.character_state.character
        if character.lvl < 10:
            return

        if recipes is None:
            recipes = self.character_state.character.recipes

        recipes = RecipeService.get_valid_ordered(
            self.service,
            [elem.id for elem in recipes],
            self.character_state.character.id,
        )

        if self.character_state.character.is_sub and len(recipes) > 0:
            self.logger.info(f"Gonna craft : {recipes}")
            self.crafter.run_crafter(recipes)

        # do not sell items that are in ingredient of craft items
        sell_items = ItemService.get_default_sellable_items(
            self.service,
            self.character_state.character.id,
            [_elem.id for _elem in recipes],
        )
        if len(sell_items) > 0:
            self.logger.info(f"Gonna sell : {sell_items}")
            self.seller.run_seller(sell_items)

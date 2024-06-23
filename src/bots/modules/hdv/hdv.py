from logging import Logger
from EzreD2Shared.shared.schemas.item import ItemSchema
from EzreD2Shared.shared.schemas.recipe import RecipeSchema

from src.bots.modules.hdv.craft import Crafter
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

    def run_hdv(
        self,
        recipes: list[RecipeSchema] | None = None,
        sell_items: list[ItemSchema] | None = None,
    ):
        if self.character_state.character.lvl < 10:
            return

        if recipes is None:
            recipes = RecipeService.get_default_recipes(
                self.service, self.character_state.character.id
            )
        if self.character_state.character.is_sub and recipes:
            self.logger.info(f"Gonna craft : {recipes}")
            self.crafter.run_crafter(recipes)

        # do not sell items that are in ingredient of craft items
        if sell_items is None:
            sell_items = ItemService.get_default_sellable_items(
                self.service,
                self.character_state.character.id,
                [elem.id for elem in recipes],
            )
        if sell_items:
            self.logger.info(f"Gonna sell : {sell_items}")
            self.seller.run_seller(sell_items)

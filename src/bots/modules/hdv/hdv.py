from EzreD2Shared.shared.schemas.item import ItemSchema
from EzreD2Shared.shared.schemas.recipe import RecipeSchema

from src.bots.modules.hdv.craft import Crafter
from src.bots.modules.hdv.sell import Seller
from src.services.item import ItemService
from src.services.recipe import RecipeService


class Hdv(Crafter, Seller):
    def run_hdv(
        self,
        recipes: list[RecipeSchema] | None = None,
        sell_items: list[ItemSchema] | None = None,
    ):
        if self.character.lvl < 10:
            return

        if recipes is None:
            recipes = RecipeService.get_default_recipes(self.character.id)
        if self.character.is_sub and recipes:
            self.log_info(f"Gonna craft : {recipes}")
            self.run_crafter(recipes)

        # do not sell items that are in ingredient of craft items
        if sell_items is None:
            sell_items = ItemService.get_default_sellable_items(
                self.character.id, [elem.id for elem in recipes]
            )
        if sell_items:
            self.log_info(f"Gonna sell : {sell_items}")
            self.run_seller(sell_items)

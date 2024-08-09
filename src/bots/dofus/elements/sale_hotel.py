from dataclasses import dataclass
from logging import Logger
from time import sleep

import numpy
import tesserocr
import win32con

from D2Shared.shared.consts.adaptative.positions import (
    HOTEL_OPEN_QUANTITY_PANEL_POSITION,
    HOTEL_PRICE_INPUT_POSITION,
    SALE_HOTEL_ALL_CATEGORY_POSITION,
    SALE_HOTEL_FILTER_OBJECTS_POSITION,
)
from D2Shared.shared.consts.adaptative.regions import (
    RIGHT_INVENTORY_SALE_HOTEL,
    SALE_HOTEL_AVAILABLE_SLOT_REGION,
    SALE_HOTEL_FIRST_PRICE_REGION,
    SALE_HOTEL_FIRST_QUANTITY_REGION,
    SALE_HOTEL_QUANTITY_REGION,
    SALE_HOTEL_SECOND_PRICE_REGION,
    SALE_HOTEL_SECOND_QUANTITY_REGION,
    SALE_HOTEL_THIRD_PRICE_REGION,
    SALE_HOTEL_THIRD_QUANTITY_REGION,
)
from D2Shared.shared.consts.object_configs import ObjectConfigs
from D2Shared.shared.enums import CategoryEnum, SaleHotelQuantity
from D2Shared.shared.schemas.item import SellItemInfo
from D2Shared.shared.schemas.region import RegionSchema
from src.bots.dofus.walker.core_walker_system import CoreWalkerSystem
from src.bots.dofus.walker.entities_map.sale_hotel import (
    get_sales_hotels_by_category,
)
from src.exceptions import UnknowStateException
from src.image_manager.ocr import (
    BASE_CONFIG,
    get_text_from_image,
    set_config_for_ocr_number,
)
from src.image_manager.screen_objects.icon_searcher import IconSearcher
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.image_manager.transformation import crop_image
from src.services.price import PriceService
from src.services.session import ServiceSession
from src.states.character_state import CharacterState
from src.utils.time import wait
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller


@dataclass
class SaleHotel:
    logger: Logger

    def sale_hotel_get_current_quantity_item(
        self, img: numpy.ndarray
    ) -> SaleHotelQuantity | None:
        """need to be in hdv & item selected, return quantity displayed

        Args:
            img (numpy.ndarray)

        Returns:
            int | None: the quantity of item displayed
        """
        img = crop_image(img, SALE_HOTEL_QUANTITY_REGION)
        with tesserocr.PyTessBaseAPI(**BASE_CONFIG) as tes_api:
            set_config_for_ocr_number(tes_api, white_list="10")
            try:
                return SaleHotelQuantity(int(get_text_from_image(img, tes_api)))
            except ValueError:
                return None

    def sale_hotel_get_area_price_by_quantity(
        self, img: numpy.ndarray, quantity: SaleHotelQuantity
    ) -> RegionSchema | None:
        """get area of price based on quantity (1, 10, 100)

        Args:
            quantity (int)


        Returns:
            Area: the area of price wanted
        """
        with tesserocr.PyTessBaseAPI(**BASE_CONFIG) as tes_api:
            tes_api.SetPageSegMode(tesserocr.PSM.SINGLE_LINE)
            tes_api.SetVariable("tessedit_char_whitelist", "10")
            for quantity_region, price_region in [
                (SALE_HOTEL_FIRST_QUANTITY_REGION, SALE_HOTEL_FIRST_PRICE_REGION),
                (SALE_HOTEL_SECOND_QUANTITY_REGION, SALE_HOTEL_SECOND_PRICE_REGION),
                (SALE_HOTEL_THIRD_QUANTITY_REGION, SALE_HOTEL_THIRD_PRICE_REGION),
            ]:
                croped_img = crop_image(img, quantity_region)
                try:
                    quantity_found = int(get_text_from_image(croped_img, tes_api))
                except ValueError:
                    continue
                if quantity_found == quantity:
                    return price_region
        return None

    def sale_hotel_get_price_by_area_item(
        self, img: numpy.ndarray, area_price: RegionSchema
    ) -> int | None:
        """get price displayed in area

        Args:
            img (numpy.ndarray)
            area_price (RegionSchema)

        Returns:
            int | None: price found, return None if invalid number
        """
        img = crop_image(img, area_price)
        with tesserocr.PyTessBaseAPI(**BASE_CONFIG) as tes_api:
            set_config_for_ocr_number(tes_api)
            try:
                price = int(get_text_from_image(img, tes_api))
            except ValueError:
                return None

        return price

    def sale_hotel_get_price_average_item(self, img: numpy.ndarray) -> float | None:
        """get price average of item based on all price show in interface\n
        it make a average from unity price, per dozen, per hundred

        Args:
            img (numpy.ndarray)

        Returns:
            float | None: the average price, or none if no price found
        """
        sum_prices: float = 0
        quantity_found: int = 0
        for quantity in SaleHotelQuantity:
            area_price = self.sale_hotel_get_area_price_by_quantity(img, quantity)
            if area_price is None:
                continue
            price = self.sale_hotel_get_price_by_area_item(img, area_price)
            if price is None:
                continue
            self.logger.info(f"Found price {price} for quantity {quantity}")
            sum_prices += price
            quantity_found += quantity

        if quantity_found == 0:
            return None
        return sum_prices / quantity_found

    def sale_hotel_get_price_item(
        self, img: numpy.ndarray, price_average: float
    ) -> tuple[int, SaleHotelQuantity] | None:
        """get price for current item in sell place

        Args:
            img (numpy.ndarray)
            price_average (float): price average of item, in case no price were found in the hud

        Returns:
            tuple[int, int] | None: prices and quantity
        """
        quantity = self.sale_hotel_get_current_quantity_item(img)
        if quantity is None:
            self.logger.info("No quantity found.")
            return None

        area_price = self.sale_hotel_get_area_price_by_quantity(img, quantity)
        if (
            area_price is not None
            and (price := self.sale_hotel_get_price_by_area_item(img, area_price))
            is not None
        ):
            self.logger.info(f"Found price {price} for quantity {quantity}")
            return price, quantity

        self.logger.info(
            f"No price found for {quantity}, calculating price from other quantities"
        )
        other_quantities = [
            other_quantity
            for other_quantity in SaleHotelQuantity
            if other_quantity != quantity
        ]
        prices = []
        # calculate price based on other quantities
        for other_quantity in other_quantities:
            area_price = self.sale_hotel_get_area_price_by_quantity(img, other_quantity)
            if area_price is None:
                continue
            price = self.sale_hotel_get_price_by_area_item(img, area_price)
            if price is not None:
                prices.append(int(price * quantity / other_quantity))

        if len(prices) > 0:
            self.logger.info(
                f"Got price from other quantities (divided for curr quantity) : {prices}"
            )
            return min(prices), quantity

        # no price display on hdv
        self.logger.info(
            "Found no price display, return average price multiplied by 1.3"
        )
        return int(quantity * price_average * 1.3), quantity

    def sale_hotel_get_count_remaining_slot(self, img: numpy.ndarray) -> int | None:
        """get count of remaining slot displayed in sale hotel

        Args:
            img (numpy.ndarray)

        Returns:
            int: count of remaining slot
        """
        croped_img = crop_image(img, SALE_HOTEL_AVAILABLE_SLOT_REGION)
        with tesserocr.PyTessBaseAPI(**BASE_CONFIG) as tes_api:
            set_config_for_ocr_number(tes_api, white_list="0123456789/")
            text = get_text_from_image(croped_img, tes_api)
        try:
            curr_slot, max_slot = text.split("/")
            return int(max_slot) - int(curr_slot)
        except ValueError:
            return None


@dataclass
class SaleHotelSystem:
    core_walker_sys: CoreWalkerSystem
    sale_hotel: SaleHotel
    controller: Controller
    capturer: Capturer
    object_searcher: ObjectSearcher
    icon_searcher: IconSearcher
    logger: Logger
    image_manager: ImageManager
    service: ServiceSession
    character_state: CharacterState

    def sale_hotel_choose_biggest_quantity(
        self,
        quantities: list[SaleHotelQuantity] = [
            SaleHotelQuantity.HUNDRED,
            SaleHotelQuantity.TEN,
            SaleHotelQuantity.ONE,
        ],
    ) -> numpy.ndarray | None:
        self.logger.info("Choosing biggest quantity")
        self.controller.click(HOTEL_OPEN_QUANTITY_PANEL_POSITION)
        sleep(0.3)
        img = self.capturer.capture()

        hundred_info = self.object_searcher.get_position(
            img, ObjectConfigs.SaleHotel.hundred_quantity
        )
        if hundred_info and SaleHotelQuantity.HUNDRED in quantities:
            self.controller.click(hundred_info[0])
            sleep(0.3)
            img = self.capturer.capture()
        elif (
            ten_info := self.object_searcher.get_position(
                img, ObjectConfigs.SaleHotel.ten_quantity
            )
        ) and SaleHotelQuantity.TEN in quantities:
            self.controller.click(ten_info[0])
            sleep(0.3)
            img = self.capturer.capture()
        elif (
            one_info := self.object_searcher.get_position(
                img, ObjectConfigs.SaleHotel.one_quantity
            )
        ) and SaleHotelQuantity.ONE in quantities:
            self.controller.click(one_info[0])
            sleep(0.3)
            img = self.capturer.capture()
        else:
            return None

        return img

    def sale_hotel_sell_items_inv(
        self, items_info_inventory: set[SellItemInfo]
    ) -> tuple[bool, list[int]]:
        """need to be in category sell in hdv, sell all item from inventory

        Returns:
            bool: True if full place, False if no more object
        """
        self.controller.click(SALE_HOTEL_ALL_CATEGORY_POSITION)

        MAX_TRY = 30
        count_remaining_slot: int | None = None
        for _ in range(MAX_TRY):
            img = self.capturer.capture()
            count_remaining_slot = self.sale_hotel.sale_hotel_get_count_remaining_slot(
                img
            )
            if count_remaining_slot is None:
                sleep(1)
                continue
            self.logger.info(f"Remaining Slots : {count_remaining_slot}")
            break
        if count_remaining_slot is None:
            raise UnknowStateException(
                self.capturer.capture(), "value_error_slot_max_try"
            )
        if count_remaining_slot == 0:
            return True, []

        if (
            self.object_searcher.get_position(img, ObjectConfigs.Check.medium_inventory)
            is None
        ):
            self.controller.click(SALE_HOTEL_FILTER_OBJECTS_POSITION)
            sleep(0.3)
            img = self.capturer.capture()

        completed_items: list[int] = []
        for item_info_inv in items_info_inventory:
            wait()
            img = self.capturer.capture()
            self.logger.info(f"Treating item : {item_info_inv}")
            pos_item_inv = self.icon_searcher.search_icon_item(
                item_info_inv.item, img, RIGHT_INVENTORY_SALE_HOTEL
            )
            if pos_item_inv is None:
                self.logger.warning(f"Did not found icon for item {item_info_inv}")
                continue
            self.controller.click(pos_item_inv)
            wait((0.8, 1.5))
            img = self.capturer.capture()
            price_average = self.sale_hotel.sale_hotel_get_price_average_item(img)
            self.logger.info(f"Got average price from hud : {price_average}")
            if price_average is None:
                continue
            price = PriceService.update_or_create_price(
                self.service,
                item_info_inv.item_id,
                self.character_state.character.server_id,
                price_average,
            )
            price_average = price.average
            self.logger.info(f"Got average price : {price_average}")

            if price_average is None:
                continue

            new_img = self.sale_hotel_choose_biggest_quantity(
                item_info_inv.sale_hotel_quantities
            )
            if new_img is None:
                continue
            img = new_img

            old_price: int | None = None
            old_quantity: int | None = None
            while True:
                price_info = self.sale_hotel.sale_hotel_get_price_item(
                    img, price_average
                )
                if price_info is None:
                    break
                curr_price, curr_quantity = price_info
                if curr_quantity not in item_info_inv.sale_hotel_quantities:
                    break

                if (
                    old_price is None
                    or old_quantity != curr_quantity
                    or abs(curr_price - old_price) > 10
                ):
                    new_price = max(curr_price - 1, 2)
                    self.controller.click(HOTEL_PRICE_INPUT_POSITION, count=2)
                    self.controller.send_text(str(new_price))
                    old_quantity = curr_quantity
                    old_price = new_price
                else:
                    self.controller.key(win32con.VK_RETURN)
                wait()
                img = self.capturer.capture()
                pos_info_yes = self.object_searcher.get_position(
                    img, ObjectConfigs.Button.yes
                )
                if pos_info_yes is not None:
                    self.logger.info("Confirming price.")
                    self.controller.click(pos_info_yes[0])
                    wait()
                    img = self.capturer.capture()

                count_remaining_slot -= 1
                if count_remaining_slot <= 0:
                    return True, completed_items
            completed_items.append(item_info_inv.item_id)
        return False, completed_items

    def go_to_sale_hotel(self, category: CategoryEnum):
        sale_hotels = get_sales_hotels_by_category(self.service, category)
        sale_hotel_entity = self.core_walker_sys.go_near_entity_map(sale_hotels)
        self.controller.click(sale_hotel_entity.position)
        pos = self.image_manager.wait_on_screen(
            ObjectConfigs.SaleHotel.sale_category, force=True
        )[0]
        self.controller.click(pos)

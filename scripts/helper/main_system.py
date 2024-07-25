import logging
import os
import sys
from logging import Logger
from threading import Event, RLock

sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from src.bots.dofus.elements.bank import BankSystem
from src.bots.dofus.hud.hud_system import Hud, HudSystem
from src.bots.dofus.hud.info_popup.job_level import JobParser
from src.bots.dofus.walker.buildings.bank_buildings import BankBuilding
from src.bots.dofus.walker.core_walker_system import CoreWalkerSystem
from src.consts import DOFUS_WINDOW_SIZE
from src.image_manager.animation import AnimationManager
from src.image_manager.screen_objects.icon_searcher import IconSearcher
from src.image_manager.screen_objects.image_manager import ImageManager
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.services.client_service import ClientService
from src.services.recipe import RecipeService
from src.states.character_state import CharacterState
from src.states.map_state import MapState
from src.window_manager.capturer import Capturer
from src.window_manager.controller import Controller
from src.window_manager.organizer import Organizer, get_windows_by_process_and_name

if __name__ == "__main__":
    logger = Logger("root")
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    service = ClientService(logger)
    for window in get_windows_by_process_and_name(target_process_name="Dofus.exe"):
        character_id = window.name.split(" - Dofus")[0]
        action_lock = RLock()
        is_paused = Event()
        hud = Hud(logger=logger)
        character_state = CharacterState(service=service, character_id=character_id)
        map_state = MapState()

        organizer = Organizer(
            window_info=window,
            is_paused=is_paused,
            target_window_size=DOFUS_WINDOW_SIZE,
            logger=logger,
        )
        capturer = Capturer(
            action_lock=action_lock,
            organizer=organizer,
            is_paused=is_paused,
            window_info=window,
            logger=logger,
        )
        controller = Controller(
            logger=logger,
            window_info=window,
            is_paused=is_paused,
            organizer=organizer,
            action_lock=action_lock,
        )
        animation_manager = AnimationManager(capturer=capturer)
        icon_searcher = IconSearcher(service=service)
        object_searcher = ObjectSearcher(service=service)
        job_parser = JobParser(service=service, logger=logger)
        image_manager = ImageManager(capturer=capturer, object_searcher=object_searcher)
        hud_sys = HudSystem(
            hud=hud,
            image_manager=image_manager,
            character_state=character_state,
            service=service,
            controller=controller,
            object_searcher=object_searcher,
            capturer=capturer,
            logger=logger,
            job_parser=job_parser,
        )
        core_walker_sys = CoreWalkerSystem(
            hud_sys=hud_sys,
            logger=logger,
            map_state=map_state,
            character_state=character_state,
            controller=controller,
            image_manager=image_manager,
            object_searcher=object_searcher,
            animation_manager=animation_manager,
            capturer=capturer,
            service=service,
        )
        bank_building = BankBuilding(
            core_walker_sys=core_walker_sys,
            logger=logger,
            controller=controller,
            image_manager=image_manager,
            service=service,
        )
        bank_sys = BankSystem(
            bank_building=bank_building,
            object_searcher=object_searcher,
            capturer=capturer,
            image_manager=image_manager,
            icon_searcher=icon_searcher,
            controller=controller,
            service=service,
            core_walker_sys=core_walker_sys,
            character_state=character_state,
            logger=logger,
        )
        recipes = RecipeService.get_default_recipes(
            service, character_state.character.id
        )
        for recipe in recipes:
            if recipe.result_item.name == "Beignet de Greuvette":
                bank_sys.bank_get_ingredients_item(recipe)
                break
        # bank_sys.bank_clear_inventory()
        # bank_sys.bank_get_ingredients_item(recipes[0])

from src.common.loggers.dofus_logger import DofusLogger
from src.consts import DOFUS_WINDOW_SIZE
from src.image_manager.screen_objects.image_manager import ImageManager
from src.states.character_state import CharacterState
from src.window_manager.controller import Controller
from src.window_manager.organizer import WindowInfo


class DofusBot(CharacterState, DofusLogger, Controller, ImageManager):
    def __init__(
        self,
        window_info: WindowInfo,
        *args,
        **kwargs,
    ) -> None:
        character_id = window_info.name.split(" - Dofus")[0]
        self.is_paused: bool = False
        self.internal_pause: bool = False
        self.is_playing: bool = False
        super().__init__(
            window_info=window_info,
            character_id=character_id,
            log_header=character_id,
            target_window_size=DOFUS_WINDOW_SIZE,
            is_paused=self.is_paused,
            *args,
            **kwargs,
        )

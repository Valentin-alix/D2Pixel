from src.consts import ANKAMA_WINDOW_SIZE
from src.image_manager.screen_objects.image_manager import ImageManager
from src.window_manager.controller import Controller


class AnkamaBot(Controller, ImageManager):
    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        self.is_paused: bool = False
        super().__init__(
            log_header="Ankama Launcher",
            target_window_size=ANKAMA_WINDOW_SIZE,
            is_paused=self.is_paused,
            *args,
            **kwargs,
        )

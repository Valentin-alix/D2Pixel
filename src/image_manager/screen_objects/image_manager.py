from threading import Lock
from typing import Literal, overload

import numpy
import win32gui
import win32ui

from D2Shared.shared.entities.object_search_config import ObjectSearchConfig
from D2Shared.shared.entities.position import Position
from D2Shared.shared.schemas.template_found import TemplateFoundPlacementSchema
from src.exceptions import UnknowStateException
from src.image_manager.analysis import are_same_image
from src.image_manager.screen_objects.cursor import (
    CursorType,
    get_cursor_images,
)
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.utils.retry import RetryTimeArgs, retry_time
from src.window_manager.capturer import Capturer


class ImageManager:
    def __init__(
        self, capturer: Capturer, object_searcher: ObjectSearcher, dc_lock: Lock
    ) -> None:
        self.object_searcher = object_searcher
        self.capturer = capturer
        self.dc_lock = dc_lock

    @overload
    def wait_multiple_or_template(
        self,
        configs: list[ObjectSearchConfig],
        retry_time_args: RetryTimeArgs = ...,
        force: Literal[False] = ...,
        map_id: int | None = ...,
    ) -> (
        tuple[Position, TemplateFoundPlacementSchema, ObjectSearchConfig, numpy.ndarray]
        | None
    ): ...

    @overload
    def wait_multiple_or_template(
        self,
        configs: list[ObjectSearchConfig],
        retry_time_args: RetryTimeArgs = ...,
        force: Literal[True] = ...,
        map_id: int | None = ...,
    ) -> tuple[
        Position, TemplateFoundPlacementSchema, ObjectSearchConfig, numpy.ndarray
    ]: ...

    def wait_multiple_or_template(
        self,
        configs: list[ObjectSearchConfig],
        retry_time_args=RetryTimeArgs(),
        force: bool = False,
        map_id: int | None = None,
    ) -> (
        tuple[Position, TemplateFoundPlacementSchema, ObjectSearchConfig, numpy.ndarray]
        | None
    ):
        def found_template() -> (
            tuple[
                Position,
                TemplateFoundPlacementSchema,
                ObjectSearchConfig,
                numpy.ndarray,
            ]
            | None
        ):
            img = self.capturer.capture()
            for config in configs:
                if (
                    pos_info := self.object_searcher.get_position(img, config, map_id)
                ) is not None:
                    return *pos_info, config, img
            return None

        res = retry_time(retry_time_args)(found_template)()
        if force is True and res is None:
            raise UnknowStateException(
                self.capturer.capture(),
                "-".join([config.ref.replace(".", "_") for config in configs]),
            )
        return res

    @overload
    def wait_on_screen(
        self,
        config: ObjectSearchConfig,
        retry_time_args: RetryTimeArgs = ...,
        force: Literal[False] = ...,
        map_id: int | None = ...,
    ) -> tuple[Position, TemplateFoundPlacementSchema, numpy.ndarray] | None: ...

    @overload
    def wait_on_screen(
        self,
        config: ObjectSearchConfig,
        retry_time_args: RetryTimeArgs = ...,
        force: Literal[True] = ...,
        map_id: int | None = ...,
    ) -> tuple[Position, TemplateFoundPlacementSchema, numpy.ndarray]: ...

    def wait_on_screen(
        self,
        config: ObjectSearchConfig,
        retry_time_args=RetryTimeArgs(),
        force: bool = False,
        map_id: int | None = None,
    ) -> tuple[Position, TemplateFoundPlacementSchema, numpy.ndarray] | None:
        def found_template() -> (
            tuple[Position, TemplateFoundPlacementSchema, numpy.ndarray] | None
        ):
            img = self.capturer.capture()
            if (
                pos_info := self.object_searcher.get_position(img, config, map_id)
            ) is not None:
                return *pos_info, img
            return None

        res = retry_time(retry_time_args)(found_template)()
        if force is True and res is None:
            raise UnknowStateException(
                self.capturer.capture(), config.ref.replace(".", "_")
            )
        return res

    @overload
    def wait_not_on_screen(
        self,
        config: ObjectSearchConfig,
        retry_time_args=RetryTimeArgs(),
        force: Literal[False] = ...,
        map_id: int | None = None,
    ) -> numpy.ndarray | None: ...

    @overload
    def wait_not_on_screen(
        self,
        config: ObjectSearchConfig,
        retry_time_args=RetryTimeArgs(),
        force: Literal[True] = ...,
        map_id: int | None = None,
    ) -> numpy.ndarray: ...

    def wait_not_on_screen(
        self,
        config: ObjectSearchConfig,
        retry_time_args=RetryTimeArgs(),
        force: bool = False,
        map_id: int | None = None,
    ) -> numpy.ndarray | None:
        res = retry_time(retry_time_args)(
            lambda: self._is_not_found_template(config, map_id)
        )()
        if force is True and res is None:
            raise UnknowStateException(
                self.capturer.capture(), config.ref.replace(".", "_")
            )
        return res

    def _is_not_found_template(
        self,
        config: ObjectSearchConfig,
        map_id: int | None = None,
        img: numpy.ndarray | None = None,
    ) -> numpy.ndarray | None:
        if img is None:
            img = self.capturer.capture()
        return self.object_searcher.is_not_on_screen(img, config, map_id)

    def is_current_cursor_of_type(self, cursor_type: CursorType) -> bool:
        icon_width, icon_height = 32, 32

        cursor_info = win32gui.GetCursorInfo()
        cursor_handle = cursor_info[1]

        with self.dc_lock:
            hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
            hbmp = win32ui.CreateBitmap()
            hbmp.CreateCompatibleBitmap(hdc, icon_width, icon_height)
            hdc = hdc.CreateCompatibleDC()
            hdc.SelectObject(hbmp)

            hdc.DrawIcon((0, 0), cursor_handle)

            bmp_str = hbmp.GetBitmapBits(True)

            img = numpy.frombuffer(bmp_str, dtype="uint8")  # type: ignore
            img.shape = (icon_width, icon_height, 4)
            img = img[..., :3]
            current_icon_img = numpy.ascontiguousarray(img)

            win32gui.DeleteObject(hbmp.GetHandle())
            hdc.DeleteDC()
            cursor_type_image = get_cursor_images()[cursor_type]

        return are_same_image(current_icon_img, cursor_type_image)

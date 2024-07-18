from typing import Literal, overload

import numpy

from D2Shared.shared.entities.object_search_config import ObjectSearchConfig
from D2Shared.shared.entities.position import Position
from D2Shared.shared.schemas.template_found import TemplateFoundPlacementSchema
from src.common.retry import RetryTimeArgs, retry_time
from src.exceptions import UnknowStateException
from src.image_manager.analysis import are_same_image
from src.image_manager.screen_objects.cursor import (
    CursorType,
    get_cursor_images,
)
from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from src.window_manager.capturer import Capturer
from src.window_manager.win32 import get_cursor_icon


class ImageManager:
    def __init__(self, capturer: Capturer, object_searcher: ObjectSearcher) -> None:
        self.object_searcher = object_searcher
        self.capturer = capturer

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
            lambda: self._not_found_template(config, map_id)
        )()
        if force is True and res is None:
            raise UnknowStateException(
                self.capturer.capture(), config.ref.replace(".", "_")
            )
        return res

    def _not_found_template(
        self,
        config: ObjectSearchConfig,
        map_id: int | None = None,
        img: numpy.ndarray | None = None,
    ) -> numpy.ndarray | None:
        if img is None:
            img = self.capturer.capture()
        return self.object_searcher.is_not_on_screen(img, config, map_id)

    def is_cursor_type(self, cursor_type: CursorType) -> bool:
        current_icon = get_cursor_icon()
        cursor_type_image = get_cursor_images()[cursor_type]

        return are_same_image(current_icon, cursor_type_image)

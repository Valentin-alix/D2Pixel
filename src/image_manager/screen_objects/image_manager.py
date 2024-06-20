from typing import Literal, overload

import numpy
from EzreD2Shared.shared.entities.object_search_config import ObjectSearchConfig
from EzreD2Shared.shared.entities.position import Position
from EzreD2Shared.shared.schemas.template_found import TemplateFoundPlacementSchema

from src.common.retry import RetryTimeArgs, retry_time
from src.exceptions import UnknowStateException
from src.image_manager.analysis import are_same_image
from src.image_manager.animation import AnimationManager
from src.image_manager.screen_objects.cursor import (
    CursorType,
    get_cursor_images,
)
from src.image_manager.screen_objects.icon_searcher import IconSearcher
from src.window_manager.win32 import get_cursor_icon


class ImageManager(IconSearcher, AnimationManager):
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
            img = self.capture()
            for config in configs:
                if (pos_info := self.get_position(img, config, map_id)) is not None:
                    return *pos_info, config, img
            return None

        res = retry_time(retry_time_args)(found_template)()
        if force is True and res is None:
            raise UnknowStateException(
                self.capture(),
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
            img = self.capture()
            if (pos_info := self.get_position(img, config, map_id)) is not None:
                return *pos_info, img
            return None

        res = retry_time(retry_time_args)(found_template)()
        if force is True and res is None:
            raise UnknowStateException(self.capture(), config.ref.replace(".", "_"))
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
            raise UnknowStateException(self.capture(), config.ref.replace(".", "_"))
        return res

    def _not_found_template(
        self, config: ObjectSearchConfig, map_id: int | None = None
    ) -> numpy.ndarray | None:
        img = self.capture()
        return self.is_not_on_screen(img, config, map_id)

    def is_cursor_type(self, cursor_type: CursorType) -> bool:
        current_icon = get_cursor_icon()
        cursor_type_image = get_cursor_images()[cursor_type]

        return are_same_image(current_icon, cursor_type_image)

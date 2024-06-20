from time import sleep
from typing import Literal, overload

import numpy
from EzreD2Shared.shared.schemas.region import RegionSchema

from src.common.retry import RetryTimeArgs, retry_time
from src.exceptions import UnknowStateException
from src.image_manager.analysis import are_image_similar
from src.image_manager.transformation import crop_image, img_to_gray
from src.window_manager.capturer import Capturer


def is_on_motion(prev_img: numpy.ndarray, new_img: numpy.ndarray) -> bool:
    if are_image_similar(prev_img, new_img):
        return False
    return True


def prepare_img_animation(
    img: numpy.ndarray, area: RegionSchema | None = None
) -> numpy.ndarray:
    if area is not None:
        img = crop_image(img, area)
    return img_to_gray(img)


class AnimationManager(Capturer):
    _prev_img: numpy.ndarray | None = None

    def _is_end_animation(
        self, region: RegionSchema | None = None, img: numpy.ndarray | None = None
    ) -> numpy.ndarray | None:
        if img is None:
            img = self.capture()

        if self._prev_img is not None:
            region_prev_img = prepare_img_animation(self._prev_img, region)
            region_new_img = prepare_img_animation(img, region)

            if not is_on_motion(region_prev_img, region_new_img):
                return img

        self._prev_img = img

        return None

    def _is_start_animation(
        self, region: RegionSchema | None = None, img: numpy.ndarray | None = None
    ) -> numpy.ndarray | None:
        if img is None:
            img = self.capture()

        if self._prev_img is not None:
            region_prev_img = prepare_img_animation(self._prev_img, region)
            region_new_img = prepare_img_animation(img, region)

            if is_on_motion(region_prev_img, region_new_img):
                return img

        self._prev_img = img

        return None

    def wait_animation_end(
        self,
        img: numpy.ndarray,
        region: RegionSchema | None = None,
        retry_time_args: RetryTimeArgs = RetryTimeArgs(
            repeat_time=0.5, wait_end=(0.3, 0.6)
        ),
    ) -> numpy.ndarray:
        self._prev_img = img
        sleep(retry_time_args.repeat_time)
        res = retry_time(retry_time_args)(lambda: self._is_end_animation(region))()
        if res is None:
            raise UnknowStateException(img, "animation_too_long")
        return res

    @overload
    def wait_animation(
        self,
        img: numpy.ndarray,
        region: RegionSchema | None = None,
        retry_time_args=RetryTimeArgs(repeat_time=0.5, wait_end=(0.3, 0.6)),
        force: Literal[True] = ...,
    ) -> numpy.ndarray: ...

    @overload
    def wait_animation(
        self,
        img: numpy.ndarray,
        region: RegionSchema | None = None,
        retry_time_args=RetryTimeArgs(repeat_time=0.5, wait_end=(0.3, 0.6)),
        force: bool = False,
    ) -> numpy.ndarray | None: ...

    def wait_animation(
        self,
        img: numpy.ndarray,
        region: RegionSchema | None = None,
        retry_time_args=RetryTimeArgs(repeat_time=0.5, wait_end=(0.3, 0.6)),
        force: bool = False,
    ) -> numpy.ndarray | None:
        self._prev_img = img
        sleep(retry_time_args.repeat_time)
        res = retry_time(retry_time_args)(lambda: self._is_start_animation(region))()
        if force and res is None:
            raise UnknowStateException(img, "animation_not_appear")
        return res

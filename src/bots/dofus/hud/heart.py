import cv2
import numpy

from src.image_manager.transformation import img_to_gray

HEART_COLOR_RANGE = [numpy.array([0, 0, 180]), numpy.array([255, 255, 255])]
LIFE_HEART = numpy.array(
    [
        [780, 896],
        [766, 888],
        [755, 888],
        [734, 905],
        [734, 921],
        [747, 944],
        [780, 966],
        [812, 947],
        [823, 923],
        [823, 901],
        [808, 889],
        [795, 888],
    ],
    dtype=numpy.int32,
)


def get_heart_ratio(img: numpy.ndarray) -> float:
    mask_heart = img_to_gray(
        cv2.drawContours(
            numpy.zeros_like(img), [LIFE_HEART], -1, (255, 255, 255), thickness=-1
        )
    )
    total_pixel_heart = cv2.countNonZero(mask_heart)
    img = cv2.bitwise_and(img, img, mask=mask_heart)
    mask_heart_red = cv2.inRange(img, HEART_COLOR_RANGE[0], HEART_COLOR_RANGE[1])

    pixel_filled = cv2.countNonZero(mask_heart_red)

    ratio = pixel_filled / total_pixel_heart

    return ratio


def is_full_life(img: numpy.ndarray) -> bool:
    return get_heart_ratio(img) > 0.85

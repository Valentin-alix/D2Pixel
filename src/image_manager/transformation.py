import cv2
import numpy
from D2Shared.shared.schemas.region import RegionSchema


def img_to_gray(img: numpy.ndarray) -> numpy.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def img_to_hsv(img: numpy.ndarray) -> numpy.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_RGB2HSV)


def img_to_bgr(img: numpy.ndarray) -> numpy.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)


def crop_image(image: numpy.ndarray, area: RegionSchema) -> numpy.ndarray:
    return image[area.top : area.bot, area.left : area.right]


def img_gray_to_binary(image: numpy.ndarray, is_adaptative=False) -> numpy.ndarray:
    if is_adaptative:
        binary_img = cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2,
        )
    else:
        _, binary_img = cv2.threshold(
            image,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )
    return binary_img


def image_to_black_white(image: numpy.ndarray, is_adaptative=False) -> numpy.ndarray:
    img_gray = img_to_gray(image)
    return img_gray_to_binary(img_gray, is_adaptative=is_adaptative)


def get_inverted_image(image: numpy.ndarray) -> numpy.ndarray:
    image = cv2.bitwise_not(image)
    return image

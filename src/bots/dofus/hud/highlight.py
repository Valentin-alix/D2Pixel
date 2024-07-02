import cv2
import numpy
from D2Shared.shared.entities.position import Position

from src.image_manager.analysis import get_contour_distance_pos
from src.image_manager.transformation import img_to_gray


def remove_highlighted_zone(
    prev_img: numpy.ndarray, img: numpy.ndarray, pos: Position | None = None
) -> numpy.ndarray:
    diff_img = img - prev_img

    gray_img = img_to_gray(diff_img)

    _zone = numpy.ones((13, 13), dtype="uint8")
    # close holes for drawing contours
    gray_img = cv2.morphologyEx(gray_img, cv2.MORPH_CLOSE, _zone)

    contours, _ = cv2.findContours(gray_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for contour in contours:
        if pos and get_contour_distance_pos(contour, pos) < 0:
            continue
        # empty the content of contour
        cv2.fillPoly(img, [contour], color=(0, 0, 0))

    return img

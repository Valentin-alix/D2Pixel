import cv2
import numpy


def get_black_masked(img: numpy.ndarray) -> numpy.ndarray:
    lower = numpy.array([0, 0, 0])
    upper = numpy.array([40, 40, 40])
    mask = cv2.inRange(img, lower, upper)
    masked_img = cv2.bitwise_and(img, img, mask=mask)
    return masked_img


def get_white_masked(img: numpy.ndarray) -> numpy.ndarray:
    lower = numpy.array([130, 130, 130])
    upper = numpy.array([255, 255, 255])
    mask = cv2.inRange(img, lower, upper)
    masked_img = cv2.bitwise_and(img, img, mask=mask)
    return masked_img


def get_yellow_masked(img: numpy.ndarray) -> numpy.ndarray:
    lower = numpy.array([0, 150, 150])
    upper = numpy.array([0, 255, 255])
    mask = cv2.inRange(img, lower, upper)
    masked_img = cv2.bitwise_and(img, img, mask=mask)
    return masked_img


def get_not_brown_masked(img: numpy.ndarray) -> numpy.ndarray:
    lower = numpy.array([50, 50, 50])
    upper = numpy.array([70, 80, 80])
    mask = cv2.bitwise_not(cv2.inRange(img, lower, upper))
    img = cv2.bitwise_and(img, img, mask=mask)
    return img

import ctypes
import sys
from ctypes import wintypes
from enum import IntEnum
from time import sleep

import win32con
import win32gui
from win32api import MAKELANGID, FormatMessage, GetLastError
from win32con import FORMAT_MESSAGE_FROM_SYSTEM, LANG_NEUTRAL, SUBLANG_DEFAULT

from D2Shared.shared.entities.position import Position
from src.consts import PAUSE
from src.window_manager.controller import get_long_param

user32 = ctypes.windll.user32
GetRawInputDeviceList = user32.GetRawInputDeviceList


class RAWINPUTDEVICELIST(ctypes.Structure):
    _fields_ = [
        (
            "hDevice",
            ctypes.c_void_p,
        ),
        ("dwType", ctypes.c_uint32),
    ]


class DeviceType(IntEnum):
    OTHER = 2
    KEYBOARD = 1
    MOUSE = 0


def get_error_message():
    error_code = GetLastError()
    error_msg = ctypes.create_unicode_buffer(256)
    result = FormatMessage(
        FORMAT_MESSAGE_FROM_SYSTEM,
        None,
        error_code,
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
        error_msg,
    )
    if result == 0:
        return f"Erreur inconnue avec le code {error_code}"
    return result


def get_devices_list():
    devices_count = ctypes.c_uint(0)
    res = GetRawInputDeviceList(
        None, ctypes.byref(devices_count), ctypes.sizeof(RAWINPUTDEVICELIST)
    )
    if res == -1:
        error_msg = get_error_message()
        print(error_msg)

    device_list = (RAWINPUTDEVICELIST * devices_count.value)()
    res = GetRawInputDeviceList(
        device_list, ctypes.byref(devices_count), ctypes.sizeof(RAWINPUTDEVICELIST)
    )
    return device_list


class RAWINPUTHEADER(ctypes.Structure):
    _fields_ = [
        ("dwType", ctypes.c_uint32),
        ("dwSize", ctypes.c_uint32),
        ("hDevice", ctypes.c_void_p),
        ("wParam", wintypes.WPARAM),
    ]


class RAWMOUSE(ctypes.Structure):
    _fields_ = [
        ("usFlags", ctypes.c_uint16),
        ("ulButtons", ctypes.c_uint32),
        ("usButtonFlags", ctypes.c_uint16),
        ("usButtonData", ctypes.c_uint16),
        ("ulRawButtons", ctypes.c_uint32),
        ("lLastX", ctypes.c_int32),
        ("lLastY", ctypes.c_int32),
        ("ulExtraInformation", ctypes.c_uint32),
    ]


class RAWINPUT(ctypes.Structure):
    _fields_ = [
        ("header", RAWINPUTHEADER),
        ("mouse", RAWMOUSE),
    ]


def raw_click(device: RAWINPUTDEVICELIST, hwnd: int, pos: Position):
    raw_input = RAWINPUT()
    raw_input.header.dwType = 0  # 0 signifie souris
    raw_input.header.dwSize = ctypes.sizeof(RAWINPUT)
    raw_input.header.hDevice = device.hDevice  # Pour une simulation, laisser à None
    raw_input.mouse.lLastX = pos.x_pos  # Exemple: mouvement en X
    raw_input.mouse.lLastY = pos.y_pos  # Exemple: mouvement en Y
    raw_input.mouse.ulButtons = 0  # Aucun bouton pressé

    # allouer de la mémoire pour rawinput
    # handle_raw = ctypes.windll.kernel32.GlobalAlloc(GHND, 64)
    # print(handle_raw)
    # # lock memory & get pointer
    # pointer_raw = ctypes.windll.kernel32.GlobalLock(handle_raw)
    # print(pointer_raw)
    # print(get_error_message())
    # ctypes.windll.kernel32.GlobalUnlock(handle_raw)
    sys.exit()
    # Copier la structure RAWINPUT dans la mémoire allouée
    ctypes.memmove(pointer_raw, ctypes.byref(raw_input), ctypes.sizeof(RAWINPUT))

    ctypes.windll.kernel32.GlobalUnlock(handle_raw)

    win32gui.PostMessage(hwnd, 0x00FF, 1, handle_raw)
    return

    ctypes.windll.kernel32.GlobalUnlock(handle_raw)

    long_param = get_long_param(pos)
    win32gui.PostMessage(
        hwnd,
        win32con.WM_LBUTTONDOWN,
        win32con.MK_LBUTTON,
        long_param,
    )
    sleep(PAUSE)
    win32gui.PostMessage(hwnd, 0x00FF, 0, handle_raw)
    sleep(PAUSE)
    win32gui.PostMessage(
        hwnd,
        win32con.WM_LBUTTONUP,
        win32con.MK_LBUTTON,
        long_param,
    )

    ctypes.windll.kernel32.GlobalFree(handle_raw)

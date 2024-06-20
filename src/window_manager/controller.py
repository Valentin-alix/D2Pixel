from contextlib import contextmanager
from threading import RLock
from time import sleep

import pyperclip
import win32api
import win32con
import win32gui
from EzreD2Shared.shared.consts.adaptative.positions import EMPTY_POSITION
from EzreD2Shared.shared.entities.position import Position
from EzreD2Shared.shared.utils.randomizer import PAUSE
from win32api import VkKeyScan

from src.exceptions import StoppedException
from src.window_manager.organizer import Organizer
from src.window_manager.win32 import (
    get_foreground_window,
    kill_window,
    set_foreground_window,
)

type Key = str | int


def get_related_wparam(char: Key) -> int:
    if isinstance(char, int):
        return char
    return VkKeyScan(char)  # type: ignore


def get_long_param(pos: Position) -> float:
    return win32api.MAKELONG(pos.x_pos, pos.y_pos)


focus_lock: RLock = RLock()


class Controller(Organizer):
    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

    def kill_window(self):
        with self.action_lock:
            kill_window(self.window_info.hwnd)

    @contextmanager
    def set_focus(self):
        if self.is_paused:
            raise StoppedException()
        try:
            focus_lock.acquire()
            if get_foreground_window() != self.window_info.hwnd:
                set_foreground_window(self.window_info.hwnd)
            yield None
        finally:
            focus_lock.release()

    def click(self, pos: Position, count: int = 1):
        if self.is_paused:
            raise StoppedException()
        with self.action_lock:
            long_param = get_long_param(pos)
            self.log_debug(f"{count} click at {pos}")
            self.adjust_window_size()
            for _ in range(count):
                win32gui.PostMessage(
                    self.window_info.hwnd,
                    win32con.WM_LBUTTONDOWN,
                    win32con.MK_LBUTTON,
                    long_param,
                )
                sleep(PAUSE)
                win32gui.PostMessage(
                    self.window_info.hwnd,
                    win32con.WM_LBUTTONUP,
                    win32con.MK_LBUTTON,
                    long_param,
                )
                sleep(PAUSE)

    def void_click(self):
        self.click(EMPTY_POSITION)

    def move(self, pos: Position):
        if self.is_paused:
            raise StoppedException()
        with (
            self.set_focus(),
            self.action_lock,
        ):  # because we need the mouse to be on window area
            self.log_debug(f"move {pos}")
            long_param = get_long_param(pos)
            self.adjust_window_size()
            win32gui.PostMessage(
                self.window_info.hwnd, win32con.WM_MOUSEMOVE, 0, long_param
            )
            sleep(0.2)

    def key_down(self, char: Key):
        if self.is_paused:
            raise StoppedException()
        with self.action_lock:
            self.log_debug(f"keydown {char}")
            w_param = get_related_wparam(char)
            win32gui.PostMessage(self.window_info.hwnd, win32con.WM_KEYDOWN, w_param, 0)
            sleep(PAUSE)

    def key_up(self, char: Key):
        if self.is_paused:
            raise StoppedException()
        with self.action_lock:
            self.log_debug(f"keyup {char}")
            w_param = get_related_wparam(char)
            win32gui.PostMessage(self.window_info.hwnd, win32con.WM_KEYUP, w_param, 0)
            sleep(PAUSE)

    def key(self, key: Key):
        if self.is_paused:
            raise StoppedException()
        with self.action_lock:
            self.key_down(key)
            self.key_up(key)

    @contextmanager
    def hold(self, key: Key):
        if self.is_paused:
            raise StoppedException()
        with self.action_lock:
            self.key_down(key)
            yield
            self.key_up(key)

    def send_text(self, text: str, with_enter=True, pos: Position | None = None):
        if self.is_paused:
            raise StoppedException()
        with self.action_lock:
            if pos is not None:
                self.click(pos)
            for char in text:
                win32gui.PostMessage(
                    self.window_info.hwnd, win32con.WM_CHAR, ord(char), 0
                )
            if with_enter:
                self.key(win32con.VK_RETURN)

    def get_selected_text(self):
        if self.is_paused:
            raise StoppedException()
        with self.action_lock:
            self.key_down(win32con.VK_CONTROL)
            self.key("c")
            self.key_up(win32con.VK_CONTROL)
            text = pyperclip.paste()
        return text

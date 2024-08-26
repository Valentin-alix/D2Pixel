from contextlib import contextmanager
from dataclasses import dataclass, field
from logging import Logger
from threading import Event, RLock
from time import sleep

import win32api
import win32con
import win32gui
from pynput.keyboard import Controller as KeyBoardController
from pynput.keyboard import Key as PyKey
from win32api import VkKeyScan

from D2Shared.shared.consts.adaptative.positions import EMPTY_POSITION
from D2Shared.shared.entities.position import Position
from src.consts import PAUSE
from src.exceptions import StoppedException
from src.window_manager.organizer import Organizer
from src.window_manager.window_info import WindowInfo

type Key = str | int


def get_related_wparam(char: Key) -> int:
    if isinstance(char, int):
        return char
    return VkKeyScan(char)  # type: ignore


def get_long_param(pos: Position) -> float:
    return win32api.MAKELONG(pos.x_pos, pos.y_pos)


focus_lock: RLock = RLock()


@dataclass
class Controller:
    logger: Logger
    window_info: WindowInfo
    is_paused_event: Event
    organizer: Organizer
    action_lock: RLock
    front_keyboard: KeyBoardController = field(
        default_factory=KeyBoardController, init=False
    )

    def kill_window(self):
        with self.action_lock:
            win32gui.PostMessage(self.window_info.hwnd, win32con.WM_CLOSE, 0, 0)

    def set_foreground(self):
        self.front_keyboard.press(PyKey.alt)
        win32gui.SetForegroundWindow(self.window_info.hwnd)
        self.front_keyboard.release(PyKey.alt)
        sleep(0.5)

    @contextmanager
    def hold_focus(self):
        if self.is_paused_event.is_set():
            raise StoppedException()
        try:
            focus_lock.acquire()
            if win32gui.GetForegroundWindow() != self.window_info.hwnd:
                self.set_foreground()
            yield None
        finally:
            focus_lock.release()

    def click(self, pos: Position, count: int = 1):
        if self.is_paused_event.is_set():
            raise StoppedException()
        with self.action_lock:
            long_param = get_long_param(pos)
            self.logger.debug(f"{count} clique sur {pos}.")
            self.organizer.adjust_window_size()
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
        if self.is_paused_event.is_set():
            raise StoppedException()
        with (
            self.hold_focus(),
            self.action_lock,
        ):  # because we need the mouse to be on window area
            self.logger.debug(f"Bouge la souris jusqu'a {pos}.")
            long_param = get_long_param(pos)
            self.organizer.adjust_window_size()
            win32gui.PostMessage(
                self.window_info.hwnd, win32con.WM_MOUSEMOVE, 0, long_param
            )
            sleep(0.2)

    def key_down(self, char: Key, l_param: int = 0):
        if self.is_paused_event.is_set():
            raise StoppedException()
        with self.action_lock:
            self.logger.debug(f"Appuie sur {char}.")
            w_param = get_related_wparam(char)
            win32gui.PostMessage(
                self.window_info.hwnd, win32con.WM_KEYDOWN, w_param, l_param
            )
            sleep(PAUSE)

    def key_up(self, char: Key, l_param: int = 0):
        if self.is_paused_event.is_set():
            raise StoppedException()
        with self.action_lock:
            self.logger.debug(f"Relache {char}.")
            w_param = get_related_wparam(char)
            win32gui.PostMessage(
                self.window_info.hwnd, win32con.WM_KEYUP, w_param, l_param
            )
            sleep(PAUSE)

    def key(self, key: Key):
        if self.is_paused_event.is_set():
            raise StoppedException()
        with self.action_lock:
            self.key_down(key)
            self.key_up(key)

    @contextmanager
    def hold(self, key: Key):
        if self.is_paused_event.is_set():
            raise StoppedException()
        with self.action_lock:
            self.key_down(key)
            sleep(0.3)
            yield
            self.key_up(key)

    def send_text(self, text: str, with_enter=True, pos: Position | None = None):
        if self.is_paused_event.is_set():
            raise StoppedException()
        with self.action_lock:
            if pos is not None:
                self.click(pos)
            for char in text:
                win32gui.PostMessage(
                    self.window_info.hwnd, win32con.WM_CHAR, ord(char), 0
                )
            sleep(PAUSE)
            if with_enter:
                self.key(win32con.VK_RETURN)

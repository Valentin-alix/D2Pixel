import os
import sys

sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))

from src.bots.dofus.dofus_bot import DofusBot
from src.data_layer.entities.position import Position
from src.window_manager.organizer import get_windows_by_process_and_name
from src.window_manager.win32 import adjust_window_size, capture

if __name__ == "__main__":
    for window in get_windows_by_process_and_name(target_process_name="Dofus.exe"):
        adjust_window_size(window.hwnd, 1920, 1009)
        img = capture(window.hwnd)
        continue
        controller = DofusBot(window_info=window)
        controller.move(Position(x_pos=1407, y_pos=916))

import os
from pathlib import Path

from dotenv import get_key

RESOURCE_FOLDER_PATH = os.path.join(Path(__file__).parent.parent, "resources")
ASSET_FOLDER_PATH = os.path.join(RESOURCE_FOLDER_PATH, "assets")

ENV_PATH = os.path.join(Path(__file__).parent.parent, ".env")

DOFUS_WINDOW_SIZE = (1920, 1009)
ANKAMA_WINDOW_SIZE = (1920, 1032)

BACKEND_URL = f"http://{get_key(ENV_PATH, "BACKEND_URL") or "localhost"}:8000"

PAUSE: float = 0.05
RANGE_DURATION_ACTIVITY: tuple[float, float] = (0.6, 1.4)
RANGE_NEW_MAP: tuple[float, float] = (1, 6)
RANGE_WAIT: tuple[float, float] = (0.3, 0.7)
RANGES_HOURS_PLAYTIME: list[tuple[str, str]] = [
    ("08:00", "12:30"),
    ("13:00", "20:30"),
    ("21:00", "23:45"),
]
START_MIN_AFK_TIME: float = 60 * 60 * 3
TIME_BETWEEN_SENTENCE: float = 60 * 30

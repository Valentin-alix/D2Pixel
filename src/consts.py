import os
from pathlib import Path

from dotenv import get_key

RESOURCE_FOLDER_PATH = os.path.join(Path(__file__).parent.parent, "resources")
ASSET_FOLDER_PATH = os.path.join(RESOURCE_FOLDER_PATH, "assets")

ENV_PATH = os.path.join(Path(__file__).parent.parent, ".env")

DOFUS_WINDOW_SIZE = (1920, 1009)
ANKAMA_WINDOW_SIZE = (1920, 1032)

BACKEND_URL = f"http://{get_key(ENV_PATH, "BACKEND_URL") or "localhost"}:8000"

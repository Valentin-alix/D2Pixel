import sys


def is_in_pyinstaller_bundle() -> bool:
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

import os


def search_for_file(filename: str) -> str:
    for root, _, files in os.walk("C:\\"):
        if filename in files:
            return os.path.join(root, filename)
    raise FileNotFoundError(f"Did not found {filename}")

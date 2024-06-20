import os

from EzreD2Shared.shared.utils.debugger import timeit


@timeit
def search_for_file(filename: str) -> str:
    for root, _, files in os.walk("C:\\"):
        if filename in files:
            print(f"found file at {os.path.join(root, filename)}")
            return os.path.join(root, filename)
    raise FileNotFoundError(f"Did not found {filename}")

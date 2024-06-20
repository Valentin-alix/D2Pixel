from enum import Enum, auto
import platform


class OSVersion(Enum):
    WINDOWS_10 = auto()
    WINDOWS_11 = auto()


def get_os_version():
    if not platform.system() == "Windows":
        raise OSError("must be windows")
    release = platform.release()
    match release:
        case "10":
            return OSVersion.WINDOWS_10
        case "11":
            return OSVersion.WINDOWS_11
        case _:
            raise OSError(f"windows {release} not yet supported")

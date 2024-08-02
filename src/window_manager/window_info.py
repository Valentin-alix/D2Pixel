from pydantic import BaseModel


class WindowInfo(BaseModel):
    hwnd: int
    name: str

    def __hash__(self) -> int:
        return self.hwnd.__hash__()

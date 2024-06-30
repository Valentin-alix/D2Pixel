from time import perf_counter, sleep
from typing import Callable, NamedTuple, Type, TypeVar

from src.common.randomizer import wait

T = TypeVar("T")

MAX_RETRY = 3


def retry_count(count: int = MAX_RETRY):
    def inner(func: Callable[..., T | None]):
        def wrapper(*args, **kwargs) -> T | None:
            for _ in range(count):
                if (result := func(*args, **kwargs)) is not None:
                    return result
            return None

        return wrapper

    return inner


def retry_force_count(exception: Type[Exception], count: int = MAX_RETRY):
    def inner(func: Callable[..., T | None]):
        def wrapper(*args, **kwargs) -> T:
            result = retry_count(count)(lambda: func(*args, **kwargs))()
            if result is None:
                raise exception()
            return result

        return wrapper

    return inner


class RetryTimeArgs(NamedTuple):
    timeout: float = 8
    offset_start: float = 0.5
    wait_end: tuple[float, float] = (0.3, 0.6)
    repeat_time: float = 0.5


def retry_time(retry_args: RetryTimeArgs = RetryTimeArgs()):
    def inner(func: Callable[..., T] | list[Callable[..., T]]):
        def wrapper(*args, **kwargs) -> None | T:
            sleep(retry_args.offset_start)
            initial_time = perf_counter()
            while perf_counter() - initial_time < retry_args.timeout:
                if isinstance(func, list):
                    for _func in func:
                        res = _func(*args, **kwargs)
                        if res is not None:
                            wait(retry_args.wait_end)
                            return res
                else:
                    res = func(*args, **kwargs)
                    if res is not None:
                        wait(retry_args.wait_end)
                        return res
                sleep(retry_args.repeat_time)

            return None

        return wrapper

    return inner

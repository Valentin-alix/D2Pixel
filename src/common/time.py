from datetime import time


def convert_time_to_seconds(value: time) -> float:
    return value.hour * 3600 + value.minute * 60 + value.second

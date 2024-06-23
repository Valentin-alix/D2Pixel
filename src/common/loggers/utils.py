import logging


class ColoredFormatter(logging.Formatter):
    GREY: str = "\x1b[38;20m"
    YELLOW: str = "\x1b[33;20m"
    RED: str = "\x1b[31;20m"
    BOLD_RED: str = "\x1b[31;1m"
    RESET: str = "\x1b[0m"
    _format: str = "%(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: GREY + _format + RESET,
        logging.INFO: GREY + _format + RESET,
        logging.WARNING: YELLOW + _format + RESET,
        logging.ERROR: RED + _format + RESET,
        logging.CRITICAL: BOLD_RED + _format + RESET,
    }

    def format(self, record) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(ColoredFormatter())

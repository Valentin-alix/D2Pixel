from contextlib import contextmanager
from requests import Response, Session
from src.common.loggers.common_logger import CommonLogger
from requests.auth import HTTPBasicAuth

logger = CommonLogger("Général")


def handle_error(rep: Response, *args, **kwargs):
    if rep.status_code != 200:
        logger.log_error(f"{rep.status_code} : Error from backed : {rep.content}")


username = "lala@example.com"
password = "string"


@contextmanager
def logged_session():
    try:
        session = Session()
        session.hooks["response"].append(handle_error)
        session.auth = HTTPBasicAuth(username, password)
        yield session
    finally:
        session.close()


@contextmanager
def unlogged_session():
    try:
        session = Session()
        session.hooks["response"].append(handle_error)
        yield session
    finally:
        session.close()

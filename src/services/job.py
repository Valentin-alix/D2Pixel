from cachetools import cached
from cachetools.keys import hashkey
from src.services.session import ServiceSession
from D2Shared.shared.schemas.job import JobSchema
from src.consts import BACKEND_URL

JOB_URL = BACKEND_URL + "/job/"


class JobService:
    @staticmethod
    @cached(cache={}, key=lambda _, text: hashkey(text))
    def find_job_by_text(service: ServiceSession, text: str) -> JobSchema | None:
        with service.logged_session() as session:
            resp = session.get(f"{JOB_URL}by_text/", params={"text": text})
            if resp.json() is None:
                return None
            return JobSchema(**resp.json())

from functools import cache
from src.services.session import logged_session
from EzreD2Shared.shared.schemas.job import JobSchema
from src.consts import BACKEND_URL

JOB_URL = BACKEND_URL + "/job/"


class JobService:
    @staticmethod
    @cache
    def find_job_by_text(text: str) -> JobSchema | None:
        with logged_session() as session:
            resp = session.get(f"{JOB_URL}by_text/", params={"text": text})
            if resp.json() is None:
                return None
            return JobSchema(**resp.json())

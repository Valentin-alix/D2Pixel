from functools import cache
from src.services.session import ServiceSession
from EzreD2Shared.shared.schemas.job import JobSchema
from src.consts import BACKEND_URL

JOB_URL = BACKEND_URL + "/job/"


class JobService(ServiceSession):
    @staticmethod
    @cache
    def find_job_by_text(service: ServiceSession, text: str) -> JobSchema | None:
        with service.logged_session() as session:
            resp = session.get(f"{JOB_URL}by_text/", params={"text": text})
            if resp.json() is None:
                return None
            return JobSchema(**resp.json())

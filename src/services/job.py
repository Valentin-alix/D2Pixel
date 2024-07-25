from cachetools import cached
from cachetools.keys import hashkey

from D2Shared.shared.schemas.job import JobSchema
from src.consts import BACKEND_URL
from src.services.client_service import ClientService

JOB_URL = BACKEND_URL + "/job/"


class JobService:
    @staticmethod
    @cached(cache={}, key=lambda _, text: hashkey(text))
    async def find_job_by_text(service: ClientService, text: str) -> JobSchema | None:
        resp = await service.session.get(f"{JOB_URL}by_text/", params={"text": text})
        if resp.json() is None:
            return None
        return JobSchema(**resp.json())

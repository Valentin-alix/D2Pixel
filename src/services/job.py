from functools import cache

import requests
from EzreD2Shared.shared.schemas.job import JobSchema

from src.consts import BACKEND_URL

JOB_URL = BACKEND_URL + "/job/"


class JobService:
    @staticmethod
    @cache
    def find_job_by_text(text: str) -> JobSchema | None:
        resp = requests.get(f"{JOB_URL}by_text/", {"text": text})
        if resp.json() is None:
            return None
        return JobSchema(**resp.json())

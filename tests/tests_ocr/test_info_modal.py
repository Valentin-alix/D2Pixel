import os
import unittest

import cv2

from EzreD2Shared.shared.consts.object_configs import ObjectConfigs
from EzreD2Shared.shared.enums import JobEnum
from src.bots.dofus.hud.info_popup.job_level import get_job_level_from_level_up

from src.image_manager.screen_objects.object_searcher import ObjectSearcher
from tests.utils import PATH_FIXTURES

PATH_FIXTURES_INFOBAR = os.path.join(PATH_FIXTURES, "hud", "infobar")


class TestInfoModal(unittest.TestCase):
    object_searcher = ObjectSearcher("temp")

    def test_lvl_up_job(self):
        FOLDER_LVL_UP_JOB = os.path.join(PATH_FIXTURES_INFOBAR, "lvl_up_job")

        LVL_JOB_BY_FILENAME: dict[str, tuple[JobEnum, int]] = {
            "1": (JobEnum.ALCHIMIST, 76),
            "2": (JobEnum.ALCHIMIST, 3),
            "3": (JobEnum.WOODCUTTER, 11),
            "4": (JobEnum.ALCHIMIST, 9),
            "5": (JobEnum.ALCHIMIST, 2),
            "6": (JobEnum.ALCHIMIST, 41),
            "7": (JobEnum.FISHERMAN, 20),
        }

        for filename in os.listdir(FOLDER_LVL_UP_JOB):
            img = cv2.imread(os.path.join(FOLDER_LVL_UP_JOB, filename))
            if lvl_up_info := self.object_searcher.get_position(
                img, ObjectConfigs.Job.level_up
            ):
                job, level = get_job_level_from_level_up(
                    img,
                    lvl_up_info[1].region,
                )
                print(job, level)
                assert LVL_JOB_BY_FILENAME[filename[:-4]] == (job.name, level), (
                    job,
                    level,
                )

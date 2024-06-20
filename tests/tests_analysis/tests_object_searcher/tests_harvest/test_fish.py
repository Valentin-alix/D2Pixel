import unittest

from tests.tests_analysis.tests_object_searcher.tests_harvest.utils import (
    get_errors_resource,
)


class TestFishAccuracy(unittest.TestCase):
    def test_small_fish(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            [
                "goujon",
                "truite",
                "poisson_chaton",
                "carpe_d_iem",
                "greuvette",
                "crabe_sourimi",
                "poisson_pane",
                "sardine_brillante",
            ]
        )
        assert (total - len(not_founds)) / total > 0.6
        assert (total - len(false_positives)) / total > 0.9

    def test_medium_fish(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            [
                "brochet",
                "kralamoure",
                "perche",
                "anguille",
                "dorade_grise",
                "perche",
                "raie_bleue",
                "lotte",
            ]
        )
        assert (total - len(not_founds)) / total > 0.8
        assert (total - len(false_positives)) / total > 0.9

    def test_big_fish(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["bar_rikain", "tanche", "requin_marteau_faucille", "morue"]
        )
        assert (total - len(not_founds)) / total > 0.6
        assert (total - len(false_positives)) / total > 0.9

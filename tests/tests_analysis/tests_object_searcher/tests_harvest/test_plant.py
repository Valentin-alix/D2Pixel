import unittest

from tests.tests_analysis.tests_object_searcher.tests_harvest.utils import (
    get_errors_resource,
)


class TestPlantAccuracy(unittest.TestCase):
    def test_ortie(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["ortie"]
        )
        assert (total - len(not_founds)) / total > 0.9
        assert (total - len(false_positives)) / total > 0.95

    def test_sauge(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["sauge"]
        )
        assert (total - len(not_founds)) / total > 0.8
        assert (total - len(false_positives)) / total > 0.95

    def test_trefle(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["trefle_a_5_feuilles"]
        )
        assert (total - len(not_founds)) / total > 0.6
        assert (total - len(false_positives)) / total > 0.95

    def test_menthe_sauvage(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["menthe_sauvage"]
        )
        assert (total - len(not_founds)) / total > 0.6
        assert (total - len(false_positives)) / total > 0.95

    def test_orchidee_freyesque(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["orchidee_freyesque"]
        )
        assert (total - len(not_founds)) / total > 0.6
        assert (total - len(false_positives)) / total > 0.95

    def test_edelweiss(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["edelweiss"]
        )
        assert (total - len(not_founds)) / total > 0.6
        assert (total - len(false_positives)) / total > 0.95

    # def test_graine_pandouille(self):
    #     (
    #     total,
    #     map_with_resource,
    #     not_found,
    #     might_false_positive,
    #     sure_false_positive,
    # ) = get_errors_resource(
    #         ["graine_de_pandouille"]
    #     )
    #     print(
    #     total,
    #     map_with_resource,
    #     not_found,
    #     might_false_positive,
    #     sure_false_positive,
    # )
    #     assert (total - len(not_founds)) / total > 0.3
    #     assert (total - len(false_positives)) / total > 0.95

    def test_ginseng(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["ginseng"]
        )
        assert (total - len(not_founds)) / total > 0.6
        assert (total - len(false_positives)) / total > 0.95

    def test_belladone(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["belladone"]
        )
        assert (total - len(not_founds)) / total > 0.6
        assert (total - len(false_positives)) / total > 0.95

    # def test_mandragore(self):
    #     (
    #     total,
    #     map_with_resource,
    #     not_found,
    #     might_false_positive,
    #     sure_false_positive,
    # ) = get_errors_resource(
    #         ["mandragore"]
    #     )
    #     print((
    #     total,
    #     map_with_resource,
    #     not_found,
    #     might_false_positive,
    #     sure_false_positive,
    # ))
    #     assert (total - len(not_founds)) / total > 0.6
    #     assert (total - len(false_positives)) / total > 0.95

    def test_perce_neige(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["perce_neige"]
        )
        assert (total - len(not_founds)) / total > 0.6
        assert (total - len(false_positives)) / total > 0.95

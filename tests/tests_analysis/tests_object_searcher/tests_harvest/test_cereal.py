import unittest

from tests.tests_analysis.tests_object_searcher.tests_harvest.utils import (
    get_errors_resource,
)


class TestCerealAccuracy(unittest.TestCase):
    def test_ble(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["ble"]
        )
        assert (total - len(not_founds)) / total > 0.85
        assert (total - len(false_positives)) / total > 0.95

    def test_orge(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["orge"]
        )
        assert (total - len(not_founds)) / total > 0.55
        assert (total - len(false_positives)) / total > 0.95

    def test_avoine(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["avoine"]
        )
        assert (total - len(not_founds)) / total > 0.3
        assert (total - len(false_positives)) / total > 0.95

    def test_houblon(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["houblon"]
        )
        assert (total - len(not_founds)) / total > 0.6
        assert (total - len(false_positives)) / total > 0.95

    def test_lin(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["lin"]
        )
        assert (total - len(not_founds)) / total > 0.6
        assert (total - len(false_positives)) / total > 0.95

    def test_seigle(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["seigle"]
        )
        assert (total - len(not_founds)) / total > 0.4
        assert (total - len(false_positives)) / total > 0.95

    def test_malt(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["malt"]
        )
        assert (total - len(not_founds)) / total > 0.3
        assert (total - len(false_positives)) / total > 0.95

    def test_chanvre(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["chanvre"]
        )
        assert (total - len(not_founds)) / total > 0.1
        assert (total - len(false_positives)) / total > 0.95

    def test_mais(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["mais"]
        )
        assert (total - len(not_founds)) / total > 0.3
        assert (total - len(false_positives)) / total > 0.95

    def test_frostiz(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["frostiz"]
        )
        assert (total - len(not_founds)) / total > 0.3
        assert (total - len(false_positives)) / total > 0.95

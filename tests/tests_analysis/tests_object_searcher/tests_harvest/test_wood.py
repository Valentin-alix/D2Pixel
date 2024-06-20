import unittest

from tests.tests_analysis.tests_object_searcher.tests_harvest.utils import (
    get_errors_resource,
)


class TestWoodAccuracy(unittest.TestCase):
    def test_frene(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["bois_de_frene"]
        )
        assert (total - len(not_founds)) / total > 0.6
        assert (total - len(false_positives)) / total > 0.9

    def test_chataignier(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["bois_de_chataignier"]
        )
        assert (total - len(not_founds)) / total > 0.6
        assert (total - len(false_positives)) / total > 0.5

    def test_noyer(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["bois_de_noyer"]
        )
        assert (total - len(not_founds)) / total > 0.6
        assert (total - len(false_positives)) / total > 0.9

    def test_chene(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["bois_de_chene"]
        )
        assert (total - len(not_founds)) / total > 0.6
        assert (total - len(false_positives)) / total > 0.8

    def test_erable(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["bois_d_erable"]
        )
        assert (total - len(not_founds)) / total > 0.5
        assert (total - len(false_positives)) / total > 0.8

    def test_bombu(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["bois_de_bombu"]
        )
        assert (total - len(not_founds)) / total > 0.4
        assert (total - len(false_positives)) / total > 0.8

    # def test_oliviolet(self):
    #     (
    #     total,
    #     map_with_resource,
    #     not_found,
    #     might_false_positive,
    #     sure_false_positive,
    # ) = get_errors_resource(
    #         ["bois_d_oliviolet"]
    #     )
    #     print((
    #     total,
    #     map_with_resource,
    #     not_found,
    #     might_false_positive,
    #     sure_false_positive,
    # ))
    #     assert (total - len(not_founds)) / total > 0.4
    #     assert (total - len(false_positives)) / total > 0.8

    def test_if(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["bois_d_if"]
        )
        assert (total - len(not_founds)) / total > 0.4
        assert (total - len(false_positives)) / total > 0.8

    def test_noisetier(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["bois_de_noisetier"]
        )
        assert (total - len(not_founds)) / total > 0.4
        assert (total - len(false_positives)) / total > 0.8

    def test_merisier(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["bois_de_merisier"]
        )
        assert (total - len(not_founds)) / total > 0.4
        assert (total - len(false_positives)) / total > 0.8

    def test_ebene(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["bois_d_ebene"]
        )
        assert (total - len(not_founds)) / total > 0.4
        assert (total - len(false_positives)) / total > 0.8

    def test_charme(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["bois_de_charme"]
        )
        assert (total - len(not_founds)) / total > 0.4
        assert (total - len(false_positives)) / total > 0.8

    def test_orme(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["bois_d_orme"]
        )
        assert (total - len(not_founds)) / total > 0.4
        assert (total - len(false_positives)) / total > 0.8

    def test_tremble(self):
        (total, not_founds, false_positives, ref_utilities) = get_errors_resource(
            ["bois_de_tremble"]
        )
        assert (total - len(not_founds)) / total > 0.4
        assert (total - len(false_positives)) / total > 0.8

# -*- coding: utf-8 -*-
from pprint import pprint
from libstat.tests import MongoTestCase
from libstat.models import CachedReport, Variable
from libstat.report_templates import ReportTemplate, Group, Row

from libstat.services.report_generation import generate_report, pre_cache_observations, pre_cache_observations_for_library_comparison_report, get_report, is_variable_to_be_included
from libstat.services import report_generation
from libstat.report_templates import report_template_base

import unittest


class TestReportGeneration(MongoTestCase):

    @unittest.skip("Skipped as data in test itself is not correct")
    def test_creates_correct_report(self):
        template = ReportTemplate(groups=[
            Group(title="some_title1",
                  rows=[Row(description="some_description1",
                            variable_key="key1")]),
            Group(title="some_title2",
                  extra="some_extra_description",
                  show_chart=False,
                  rows=[Row(description="some_description2",
                            variable_key="key2",
                            computation=(lambda a, b: (a / b)),
                            variable_keys=["key1", "key2"]),
                        Row(description="only_a_label",
                            label_only=True),
                        Row(description="some_description3",
                            computation=(lambda a, b: (a / b) / 15),
                            variable_keys=["key1", "key2"]),
                        Row(description="some_description4",
                            variable_key="does_not_exist1"),
                        Row(description="some_description5",
                            variable_key="key4",
                            is_sum=True),
                        Row(description="some_description6",
                            computation=(lambda a, b: (a / b)),
                            variable_keys=["does_not_exist2", "does_not_exist3"]),
                  ])
        ])
        variable1 = self._dummy_variable(key="key1", target_groups=["folkbib"])
        variable2 = self._dummy_variable(key="key2", target_groups=["folkbib"])
        variable4 = self._dummy_variable(key="key4", target_groups=["folkbib"])
        observations = {
            "key1": {
                2012: 19.0,
                2013: 5.0,
                2014: 7.0,
                "total": 31.0,
                "incomplete_data": []
            },
            "key2": {
                2013: 11.0,
                2014: 13.0,
                "total": 47.0,
                "incomplete_data": [2012]
            },
            "key4": {
                2014: 3.0,
                2012: 17.0,
                "incomplete_data": [2013]
            }
        }

        report = generate_report(template, 2014, observations, ["folkbib"])
        expected_report = [
            {
                "title": "some_title1",
                "years": ["2012", "2013", "2014"],
                "show_chart": True,
                "rows": [
                    {
                        "label": "some_description1",
                        "show_in_chart": True,
                        "2012": 19.0,
                        "2013": 5.0,
                        "2014": 7.0,
                        "diff": ((7.0 / 5.0) - 1) * 100,
                        "nation_diff": (7.0 / 31.0) * 1000,
                    }
                ]
            },
            {
                "title": "some_title2",
                "show_chart": False,
                "extra": "some_extra_description",
                "years": ["2012", "2013", "2014"],
                "rows": [
                    {
                        "label": "some_description2",
                        "show_in_chart": True,
                        "2013": 11.0,
                        "2014": 13.0,
                        "diff": ((13.0 / 11.0) - 1) * 100,
                        "nation_diff": (13.0 / 47.0) * 1000,
                        "extra": (7.0 / 13.0) * 100,
                        "incomplete_data": ["2012"]
                    },
                    {
                        "label": "only_a_label",
                        "label_only": True,
                        "show_in_chart": False
                    },
                    {
                        "label": "some_description3",
                        "2013": (5.0 / 11.0) / 15,
                        "2014": (7.0 / 13.0) / 15,
                        "diff": (((7.0 / 13.0) / 15) / ((5.0 / 11.0) / 15) - 1) * 100,
                        "incomplete_data": ["2012"],
                        "is_key_figure": True,
                        "show_in_chart": False
                    },
                    {
                        "label": "some_description4",
                        "show_in_chart": True,
                    },
                    {
                        "label": "some_description5",
                        "show_in_chart": True,
                        "2012": 17.0,
                        "2014": 3.0,
                        "is_sum": True,
                        "incomplete_data": ["2013"]
                    },
                    {
                        "label": "some_description6",
                        "is_key_figure": True,
                        "show_in_chart": False
                    }
                ]
            }
        ]

        self.assertEqual(report, expected_report)

    def test_parses_observations_from_surveys(self):
        variable1 = self._dummy_variable(key="key1")
        variable2 = self._dummy_variable(key="key2")
        variable3 = self._dummy_variable(key="key3")

        library1 = self._dummy_library(sigel="sigel1")
        library2 = self._dummy_library(sigel="sigel2")
        library3 = self._dummy_library(sigel="sigel3")

        survey1 = self._dummy_survey(
            sample_year=2016,
            library=library1,
            observations=[
                self._dummy_observation(variable=variable1, value=1),
                self._dummy_observation(variable=variable2, value=2)
            ])

        survey2 = self._dummy_survey(
            sample_year=2016,
            library=library2,
            observations=[
                self._dummy_observation(variable=variable1, value=3),
                self._dummy_observation(variable=variable3, value=5)
            ])

        survey3 = self._dummy_survey(
            sample_year=2016,
            library=library3,
            observations=[
                self._dummy_observation(variable=variable2, value=13),
                self._dummy_observation(variable=variable3, value=17)
            ])

        survey4 = self._dummy_survey(
            sample_year=2015,
            library=library1,
            observations=[
                self._dummy_observation(variable=variable1, value=7),
                self._dummy_observation(variable=variable2, value=11)
            ])

        survey5 = self._dummy_survey(
            sample_year=2015,
            library=library2,
            observations=[
                self._dummy_observation(variable=variable1, value=8),
                self._dummy_observation(variable=variable2, value=9)
            ])

        survey6 = self._dummy_survey(
            sample_year=2014,
            library=library1,
            observations=[
                self._dummy_observation(variable=variable1, value=19),
                self._dummy_observation(variable=variable2, value=23)
            ])

        survey7 = self._dummy_survey(
            sample_year=2014,
            library=library2,
            observations=[
                self._dummy_observation(variable=variable1, value=21),
                self._dummy_observation(variable=variable2, value=22)
            ])

        survey1.publish()
        survey2.publish()
        survey3.publish()
        survey4.publish()
        survey5.publish()
        survey6.publish()
        survey7.publish()

        template = ReportTemplate(groups=[
            Group(rows=[Row(variable_key="key1")]),
            Group(rows=[Row(variable_key="key2"),
                        Row(variable_keys=["key3", "key2"]),
            ])
        ])

        observations = pre_cache_observations(template, [survey1, survey2], 2016)
        expected_observations = {
            "key1": {
                2014: (19.0 + 21.0),
                2015: (7.0 + 8.0),
                2016: (1.0 + 3.0),
                "total": (1.0 + 3.0),
                "incomplete_data": []
            },
            "key2": {
                2014: (23.0 + 22.0),
                2015: (11.0 + 9.0),
                2016: 2.0,
                "total": (2.0 + 13.0),
                "incomplete_data": [2016]
            },
            "key3": {
                2014: None,
                2015: None,
                2016: 5.0,
                "total": (5.0 + 17.0),
                "incomplete_data": [2016, 2015, 2014]
            }
        }

        self.assertEqual(observations, expected_observations)

    @unittest.skip("Skipped due to strange bson conversion error")
    def test_is_variable_to_be_included(self):
        variable1 = self._dummy_variable(key="key4", target_groups=["folkbib", "natbib"])
        variable2 = self._dummy_variable(key="key5", target_groups=["natbib"])
        variable3 = self._dummy_variable(key="key6", target_groups=["skolbib", "folkbib"])

        self.assertTrue(is_variable_to_be_included(variable1, ["folkbib"]))
        self.assertFalse(is_variable_to_be_included(variable2, ["folkbib"]))
        self.assertFalse(is_variable_to_be_included(variable3, ["folkbib", "natbib"]))


class TestReportTemplate(MongoTestCase):
    def test_returns_all_variable_keys_present_in_report_template_without_duplicates(self):
        template = ReportTemplate(groups=[
            Group(rows=[
                Row(variable_key="key1")]),
            Group(rows=[
                Row(variable_key="key2"),
                Row(variable_keys=["key3", "key2"]),
                Row(variable_key="key4", variable_keys=["key3", "key5"]),
            ])
        ])

        variable_keys = template.all_variable_keys

        self.assertEqual(len(variable_keys), 5)
        self.assertTrue("key1" in variable_keys)
        self.assertTrue("key2" in variable_keys)
        self.assertTrue("key3" in variable_keys)
        self.assertTrue("key4" in variable_keys)
        self.assertTrue("key5" in variable_keys)

    def test_fetches_description_from_variable_if_variable_exists_and_no_description_is_given(self):
        variable = self._dummy_variable(question_part="some_description")
        row = Row(variable_key=variable.key)

        self.assertEqual(row.description, variable.question_part)

    def test_does_not_fetch_description_from_variable_if_no_variable_key_is_given(self):
        row = Row()

        self.assertEqual(row.description, None)

    def test_does_not_fetch_description_from_variable_if_variable_exists_and_description_is_given(self):
        variable = self._dummy_variable(question_part="dont use this")
        row = Row(variable_key=variable.key, description="some_description")

        self.assertEqual(row.description, "some_description")

    def test_row_computes_value(self):
        row = Row(computation=(lambda a, b, c: (a / (b + c))))

        self.assertEqual(row.compute([3.0, 7.0, 11.0]), 3.0 / (7.0 + 11.0))

    def test_row_does_not_compute_with_none_values(self):
        row = Row(computation=(lambda a, b, c: (a + b + c)))

        self.assertEqual(row.compute([3.0, None, 7.0]), None)

    def test_row_handles_division_by_zero(self):
        row = Row(computation=(lambda a, b: (a / b)))

        self.assertEqual(row.compute([3.0, 0]), None)


class TestReportCaching(MongoTestCase):
    def setUp(self):
        report_template = report_template_base()
        for var in report_template.all_variable_keys:
            self._dummy_variable(key=var)

    def test_stores_cached_report_after_generation(self):
        survey1 = self._dummy_survey(sample_year=2014, publish=True)
        survey2 = self._dummy_survey(sample_year=2014, publish=True)

        surveys = [survey1, survey2]

        get_report(surveys, 2014)

        self.assertEqual(CachedReport.objects.count(), 1)

    def test_does_not_cache_same_report_twice(self):
        survey1 = self._dummy_survey(sample_year=2014, publish=True)
        survey2 = self._dummy_survey(sample_year=2014, publish=True)

        surveys = [survey1, survey2]

        get_report(surveys, 2014)
        get_report(surveys, 2014)

        self.assertEqual(CachedReport.objects.count(), 1)

    def test_returns_new_report_from_subset_of_surveys_of_cached_report(self):
        survey1 = self._dummy_survey(sample_year=2014, publish=True)
        survey2 = self._dummy_survey(sample_year=2014, publish=True)

        report1 = get_report([survey1, survey2], 2014)
        report2 = get_report([survey1], 2014)

        self.assertNotEqual(report1["id"], report2["id"])

    def test_generates_unique_id_for_different_reports(self):
        survey1 = self._dummy_survey(sample_year=2014, publish=True)
        survey2 = self._dummy_survey(sample_year=2014, publish=True)

        report1 = get_report([survey1], 2014)
        report2 = get_report([survey2], 2014)

        self.assertNotEqual(report1["id"], report2["id"])

    def test_caching_does_not_break_report(self):
        survey1 = self._dummy_survey(sample_year=2014, publish=True)
        survey2 = self._dummy_survey(sample_year=2014, publish=True)

        surveys = [survey1, survey2]

        report = get_report(surveys, 2014)

        cached_report = get_report(surveys, 2014)

        self.assertEqual(report, cached_report)

    def test_returns_cached_report_when_cache_hit(self):
        survey1 = self._dummy_survey(sample_year=2014, publish=True)
        survey2 = self._dummy_survey(sample_year=2014, publish=True)

        surveys = [survey1, survey2]

        get_report(surveys, 2014)
        report = get_report(surveys, 2014)

        self.assertEqual(CachedReport.objects.all()[0].report["id"], report["id"])

    def test_removes_all_reports_after_a_survey_has_been_published(self):
        survey1 = self._dummy_survey(sample_year=2014, publish=True, observations=[self._dummy_observation()])
        survey2 = self._dummy_survey(sample_year=2014, publish=True, observations=[self._dummy_observation()])

        get_report([survey1], 2014)
        get_report([survey2], 2014)

        survey3 = self._dummy_survey(sample_year=2014, publish=True, observations=[self._dummy_observation()])

        report = get_report([survey3], 2014)

        self.assertEqual(CachedReport.objects.count(), 1)
        self.assertEqual(CachedReport.objects.all()[0].report["id"], report["id"])

    def test_removes_all_reports_after_a_survey_has_been_republished(self):
        survey1 = self._dummy_survey(sample_year=2014, publish=True, observations=[self._dummy_observation()])
        survey2 = self._dummy_survey(sample_year=2014, publish=True, observations=[self._dummy_observation()])

        get_report([survey1], 2014)
        get_report([survey2], 2014)

        survey1.observations[0].value = u"new_value"
        survey1.publish()

        report = get_report([survey2], 2014)

        self.assertEqual(CachedReport.objects.count(), 1)
        self.assertEqual(CachedReport.objects.all()[0].report["id"], report["id"])

    def test_removes_all_reports_after_a_variable_has_been_updated(self):
        variable = self._dummy_variable()
        survey1 = self._dummy_survey(sample_year=2014, publish=True, observations=[self._dummy_observation()])
        survey2 = self._dummy_survey(sample_year=2014, publish=True, observations=[self._dummy_observation()])

        get_report([survey1], 2014)
        get_report([survey2], 2014)

        variable.description = u"something_new"
        variable.save()
        report = get_report([survey2], 2014)

        self.assertEqual(CachedReport.objects.count(), 1)
        self.assertEqual(CachedReport.objects.all()[0].report["id"], report["id"])

    def test_removes_older_reports_when_limit_reached(self):
        survey1 = self._dummy_survey(sample_year=2014, publish=True, observations=[self._dummy_observation()])
        survey2 = self._dummy_survey(sample_year=2014, publish=True, observations=[self._dummy_observation()])
        survey3 = self._dummy_survey(sample_year=2014, publish=True, observations=[self._dummy_observation()])
        survey4 = self._dummy_survey(sample_year=2014, publish=True, observations=[self._dummy_observation()])

        report_generation.REPORT_CACHE_LIMIT = 3

        report1 = get_report([survey1], 2014)
        report2 = get_report([survey2], 2014)
        report3 = get_report([survey3], 2014)
        report4 = get_report([survey4], 2014)

        self.assertEqual(CachedReport.objects.count(), 3)
        self.assertEqual(CachedReport.objects.all()[0].report["id"], report4["id"])
        self.assertEqual(CachedReport.objects.all()[1].report["id"], report3["id"])
        self.assertEqual(CachedReport.objects.all()[2].report["id"], report2["id"])


class TestLibraryComparisonReport(MongoTestCase):

    def setUp(self):
        report_template = report_template_base()
        for var in report_template.all_variable_keys:
            self._dummy_variable(key=var)

    def test_pre_cache_observations_for_library_comparison_report(self):
        beman_service_01_var = Variable.objects.filter(key="BemanService01").first()
        integrerad_01_var = Variable.objects.filter(key="Integrerad01").first()
        utlan_301_var = Variable.objects.filter(key="Utlan301").first()

        observations1 = [self._dummy_observation(variable=beman_service_01_var, value=3),
                         self._dummy_observation(variable=integrerad_01_var, value=1)]
        library1 = self._dummy_library(name='Library 1', sigel="lib1")
        survey1 = self._dummy_survey(sample_year=2015, publish=True, library=library1, observations=observations1)

        observations2 = [self._dummy_observation(variable=beman_service_01_var, value=5)]
        library2 = self._dummy_library(name='Library 2', sigel="lib2")
        survey2 = self._dummy_survey(sample_year=2015, publish=True, library=library2, observations=observations2)

        observations3 = [self._dummy_observation(variable=beman_service_01_var, value=6),
                         self._dummy_observation(variable=utlan_301_var, value=600)]
        library3 = self._dummy_library(name='Library 3', sigel="lib3")
        survey3 = self._dummy_survey(sample_year=2015, publish=True, library=library3, observations=observations3)

        surveys = [survey1, survey2, survey3]
        report_template = report_template_base()

        returns = pre_cache_observations_for_library_comparison_report(report_template, surveys, 2015)

        self.assertIsNotNone(returns['lib1'])
        self.assertIsNotNone(returns['lib3']['name'])
        self.assertEqual(returns['lib1']['name'], u'Library 1 (lib1)')
        self.assertEqual(returns['lib3']['name'], u'Library 3 (lib3)')
        self.assertEqual(returns['lib1']['Integrerad01'], 1)
        self.assertEqual(returns['lib2']['BemanService01'], 5)
        self.assertEqual(returns['lib3']['Utlan301'], 600)
        self.assertIsNone(returns['lib1']['Publ204'])
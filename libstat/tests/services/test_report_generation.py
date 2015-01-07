# -*- coding: utf-8 -*-
from pprint import pprint
from libstat.report_templates import ReportTemplate, Group, Row
from libstat.services.report_generation import generate_report, pre_cache_observations
from libstat.tests import MongoTestCase


class TestReportGeneration(MongoTestCase):
    def test_creates_correct_report(self):
        template = ReportTemplate(groups=[
            Group(title="some_title1",
                  rows=[Row(description="some_description1",
                            variable_key="key1")]),
            Group(title="some_title2",
                  extra="some_extra_description",
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
        observations = {
            "key1": {
                2012: 19.0,
                2013: 5.0,
                2014: 7.0,
                "total": 31.0
            },
            "key2": {
                2013: 11.0,
                2014: 13.0,
                "total": 47.0
            },
            "key4": {
                2014: 3.0,
                2012: 17.0
            }
        }

        report = generate_report(template, 2014, observations)
        expected_report = [
            {
                "title": "some_title1",
                "years": [2012, 2013, 2014],
                "rows": [
                    {
                        "label": "some_description1",
                        2012: 19.0,
                        2013: 5.0,
                        2014: 7.0,
                        "diff": ((7.0 / 5.0) - 1) * 100,
                        "nation_diff": (7.0 / 31.0) * 1000,
                    }
                ]
            },
            {
                "title": "some_title2",
                "extra": "some_extra_description",
                "years": [2012, 2013, 2014],
                "rows": [
                    {
                        "label": "some_description2",
                        2013: 11.0,
                        2014: 13.0,
                        "diff": ((13.0 / 11.0) - 1) * 100,
                        "nation_diff": (13.0 / 47.0) * 1000,
                        "extra": (7.0 / 13.0) * 100
                    },
                    {
                        "label": "only_a_label",
                        "label_only": True
                    },
                    {
                        "label": "some_description3",
                        2013: (5.0 / 11.0) / 15,
                        2014: (7.0 / 13.0) / 15,
                        "diff": (((7.0 / 13.0) / 15) / ((5.0 / 11.0) / 15) - 1) * 100
                    },
                    {
                        "label": "some_description4"
                    },
                    {
                        "label": "some_description5",
                        2012: 17.0,
                        2014: 3.0,
                        "is_sum": True
                    },
                    {
                        "label": "some_description6"
                    }
                ]
            }
        ]

        self.assertEqual(report, expected_report)

    def test_parses_observations_from_surveys(self):
        variable1 = self._dummy_variable(key="key1")
        variable2 = self._dummy_variable(key="key2")
        variable3 = self._dummy_variable(key="key3")

        library1 = self._dummy_library()
        library2 = self._dummy_library()
        library3 = self._dummy_library()

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
            sample_year=2014,
            library=library1,
            observations=[
                self._dummy_observation(variable=variable1, value=19),
                self._dummy_observation(variable=variable2, value=23)
            ])

        survey1.publish()
        survey2.publish()
        survey3.publish()
        survey4.publish()
        survey5.publish()

        template = ReportTemplate(groups=[
            Group(rows=[Row(variable_key="key1")]),
            Group(rows=[Row(variable_key="key2"),
                        Row(variable_keys=["key3", "key2"]),
                        Row(variable_key="does_not_exist1"),
                        Row(variable_keys=["does_not_exist2", "does_not_exist3"]),
            ])
        ])

        observations = pre_cache_observations(template, [survey1, survey2], 2016)
        expected_observations = {
            "key1": {
                2014: 19.0,
                2015: 7.0,
                2016: (1.0 + 3.0),
                "total": (1.0 + 3.0)
            },
            "key2": {
                2014: 23.0,
                2015: 11.0,
                2016: 2.0,
                "total": (2.0 + 13.0)
            },
            "key3": {
                2014: 0.0,
                2015: 0.0,
                2016: 5.0,
                "total": (5.0 + 17.0)
            }
        }

        self.assertEqual(observations, expected_observations)


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

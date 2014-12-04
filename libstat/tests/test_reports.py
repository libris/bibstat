# -*- coding: utf-8 -*-
from pprint import pprint

from libstat.reports import generate_report, ReportTemplate, Group, VariableRow, KeyFigureRow, _get_observations_from
from libstat.tests import MongoTestCase


class TestReports(MongoTestCase):
    def test_creates_correct_report(self):
        template = ReportTemplate(groups=[
            Group(title="some_title1",
                  rows=[VariableRow(description="some_description1",
                                    variable_key="key1")]),
            Group(title="some_title2",
                  rows=[VariableRow(description="some_description2",
                                    variable_key="key2"),
                        KeyFigureRow(description="some_description3",
                                     computation=(lambda a, b: (a / b) / 15),
                                     variable_keys=["key1", "key2"]),
                        VariableRow(description="some_description4",
                                    variable_key="does_not_exist1"),
                        VariableRow(description="some_description5",
                                    variable_key="key4"),
                        KeyFigureRow(description="some_description6",
                                     computation=(lambda a, b: (a / b)),
                                     variable_keys=["does_not_exist2", "does_not_exist3"]),
                  ])
        ])
        observations = {
            "key1": {
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
                2014: 3.0
            }
        }

        report = generate_report(template, 2014, observations)
        expected_report = [
            {
                "title": "some_title1",
                "years": [2013, 2014],
                "rows": [
                    {
                        "label": "some_description1",
                        2013: 5.0,
                        2014: 7.0,
                        "diff": ((7.0 / 5.0) - 1) * 100,
                        "nation_diff": (7.0 / 31.0) * 1000
                    }
                ]
            },
            {
                "title": "some_title2",
                "years": [2013, 2014],
                "rows": [
                    {
                        "label": "some_description2",
                        2013: 11.0,
                        2014: 13.0,
                        "diff": ((13.0 / 11.0) - 1) * 100,
                        "nation_diff": (13.0 / 47.0) * 1000
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
                        2014: 3.0
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
            sample_year=2015,
            library=library1,
            observations=[
                self._dummy_observation(variable=variable1, value=1),
                self._dummy_observation(variable=variable2, value=2)
            ])

        survey2 = self._dummy_survey(
            sample_year=2015,
            library=library2,
            observations=[
                self._dummy_observation(variable=variable1, value=3),
                self._dummy_observation(variable=variable3, value=5)
            ])

        survey3 = self._dummy_survey(
            sample_year=2015,
            library=library3,
            observations=[
                self._dummy_observation(variable=variable2, value=13),
                self._dummy_observation(variable=variable3, value=17)
            ])

        survey4 = self._dummy_survey(
            sample_year=2014,
            library=library1,
            observations=[
                self._dummy_observation(variable=variable1, value=7),
                self._dummy_observation(variable=variable2, value=11)
            ])

        survey1.publish()
        survey2.publish()
        survey3.publish()
        survey4.publish()

        observations = _get_observations_from([survey1, survey2], 2015)
        expected_observations = {
            u"key1": {
                2014: 7.0,
                2015: (1.0 + 3.0),
                "total": (1.0 + 3.0)
            },
            u"key2": {
                2014: 11.0,
                2015: 2.0,
                "total": (2.0 + 13.0)
            },
            u"key3": {
                2014: 0.0,
                2015: 5.0,
                "total": (5.0 + 17.0)
            }
        }

        self.assertEqual(observations, expected_observations)




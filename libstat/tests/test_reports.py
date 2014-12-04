# -*- coding: utf-8 -*-

from libstat.reports import generate_report, ReportTemplate, Group, VariableRow, KeyFigureRow
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
            [
                ["some_title1", 2013, 2014],
                ["some_description1", 5.0, 7.0, ((7.0 / 5.0) - 1) * 100, (7.0 / 31.0) * 1000]
            ],
            [
                ["some_title2", 2013, 2014],
                ["some_description2", 11.0, 13.0, ((13.0 / 11.0) - 1) * 100, (13.0 / 47.0) * 1000],
                ["some_description3", (5.0 / 11.0) / 15, (7.0 / 13.0) / 15,
                 (((7.0 / 13.0) / 15) / ((5.0 / 11.0) / 15) - 1) * 100, None],
                ["some_description4", None, None, None, None],
                ["some_description5", None, 3.0, None, None],
                ["some_description6", None, None, None, None]
            ]
        ]
        self.assertEqual(report, expected_report)
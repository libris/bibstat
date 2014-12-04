# -*- coding: utf-8 -*-
from pprint import pprint

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
                        "diff": (((7.0 / 13.0) / 15) / ((5.0 / 11.0) / 15) - 1) * 100,
                        "nation_diff": None
                    },
                    {
                        "label": "some_description4",
                        2013: None,
                        2014: None,
                        "diff": None,
                        "nation_diff": None
                    },
                    {
                        "label": "some_description5",
                        2013: None,
                        2014: 3.0,
                        "diff": None,
                        "nation_diff": None
                    },
                    {
                        "label": "some_description6",
                        2013: None,
                        2014: None,
                        "diff": None,
                        "nation_diff": None
                    }
                ]
            }
        ]
        
        self.assertEqual(report, expected_report)







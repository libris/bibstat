# -*- coding: UTF-8 -*-
from libstat.tests import MongoTestCase

from libstat.models import Cell, Row, Group
from libstat.survey_templates import survey_template, _survey_template_2014


class TestSurveyTemplate(MongoTestCase):

    def test_group_has_correct_question(self):
        group = Group(rows=[Row(cells=[
            Cell(variable_key=self._dummy_variable(key="var1_key", question="sample_question_text").key)])
        ])

        self.assertEquals(group.description, "sample_question_text")

    def test_group_has_correct_headers(self):
        group = Group(rows=[Row(cells=[
            Cell(variable_key=self._dummy_variable(key="var1_key", category="header1").key),
            Cell(variable_key=self._dummy_variable(key="var2_key", category="header2").key),
            Cell(variable_key=self._dummy_variable(key="var3_key", category="header3").key),
        ])])

        self.assertEquals(group.headers, ["header1", "header2", "header3"])

    def test_group_has_correct_number_of_columns(self):
        group = Group(rows=[Row(cells=[
            Cell(variable_key=self._dummy_variable(key="var1_key").key),
            Cell(variable_key=self._dummy_variable(key="var2_key").key),
            Cell(variable_key=self._dummy_variable(key="var3_key").key),
            Cell(variable_key=self._dummy_variable(key="var4_key").key),
        ])])

        self.assertEquals(group.columns, 4)

    def test_row_has_correct_description(self):
        row = Row(cells=[
            Cell(variable_key=self._dummy_variable(key="var1_key", sub_category="row_description1").key),
            Cell(variable_key=self._dummy_variable(key="var2_key").key),
            Cell(variable_key=self._dummy_variable(key="var3_key").key),
        ])

        self.assertEquals(row.description, "row_description1")

    def test_cell_has_correct_explanation(self):
        cell = Cell(variable_key=self._dummy_variable(key="var1_key", description="var1_sample_description").key)

        self.assertEquals(cell.explanation, "var1_sample_description")

    def test_returns_template_for_2014(self):
        template = survey_template(2014)

        self.assertEquals(template, _survey_template_2014())

    def test_returns_2014_template_for_2015(self):
        template = survey_template(2015)

        self.assertEquals(template, _survey_template_2014())

    def test_returns_default_template_for_2013(self):
        survey = self._dummy_survey(observations=[
            self._dummy_observation(),
            self._dummy_observation(),
            self._dummy_observation(),
        ])
        template = survey_template(2013, survey)

        self.assertEquals(len(template.cells), 3)

    def test_returns_empty_template_for_2013_without_survey(self):
        template = survey_template(2013)

        self.assertEquals(len(template.cells), 0)

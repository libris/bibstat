# -*- coding: UTF-8 -*-
from django.forms import CharField, IntegerField, ChoiceField, DecimalField

from libstat.tests import MongoTestCase
from libstat.models import Variable, SurveyResponse, SurveyObservation
from libstat.forms import SurveyObservationsForm


"""
    Form test cases
"""


class SurveyObservationsFormTest(MongoTestCase):
    def setUp(self):
        v1 = Variable(key=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", type=u"integer",
                      is_public=True, target_groups=[u"public"])
        v1.save()
        v2 = Variable(key=u"folk6",
                      description=u"Är huvudbiblioteket i er kommun integrerat med ett skolbibliotek? 1=ja",
                      type=u"boolean", is_public=True, target_groups=[u"public"])
        v2.save()
        v3 = Variable(key=u"folk8", description=u"Textkommentar", type=u"string", is_public=False,
                      target_groups=[u"public"])
        v3.save()
        v4 = Variable(key=u"folk35", description=u"Antal årsverken övrig personal", type=u"decimal", is_public=True,
                      target_groups=[u"public"])
        v4.save()
        v5 = Variable(key=u"folk52", description=u"Andel tryckt skönlitteratur", type=u"percent", is_public=True,
                      target_groups=[u"public"])
        v5.save()
        v6 = Variable(key=u"folk38", description=u"Total driftskostnad", type=u"long", is_public=True,
                      target_groups=[u"public"])
        v6.save()

        sr = SurveyResponse(library_name=u"BIBLIOTEKEN I RAGUNDA", sample_year=2013, target_group="public",
                            observations=[])
        sr.observations.append(
            SurveyObservation(variable=v1, value=7.013, _source_key="folk5", _is_public=v1.is_public))
        sr.observations.append(SurveyObservation(variable=v2, value=None, _source_key="folk6", _is_public=v2.is_public))
        sr.observations.append(
            SurveyObservation(variable=v3, value=u"Här är en kommentar", _source_key="folk8", _is_public=v3.is_public))
        sr.observations.append(
            SurveyObservation(variable=v4, value=4.76593020050, _source_key=u"folk35", _is_public=v4.is_public))
        sr.observations.append(
            SurveyObservation(variable=v5, value=0.57306940, _source_key=u"folk52", _is_public=v5.is_public))
        sr.observations.append(
            SurveyObservation(variable=v6, value=49130498.0, _source_key=u"folk38", _is_public=v6.is_public))

        self.survey_response = sr.save()
        self.obs_folk5 = self.survey_response.observations[0]
        self.obs_folk6 = self.survey_response.observations[1]
        self.obs_folk8 = self.survey_response.observations[2]
        self.obs_folk35 = self.survey_response.observations[3]
        self.obs_folk52 = self.survey_response.observations[4]
        self.obs_folk38 = self.survey_response.observations[5]

    def test_form_instance_should_dynamically_add_fields_for_each_observation_in_instance(self):
        form = SurveyObservationsForm(instance=self.survey_response)
        self.assertEquals(len(form.fields), 6)

    def test_form_should_transform_observation_values_to_correct_type(self):
        form = SurveyObservationsForm(instance=self.survey_response)

        self.assertEquals(form.fields[u"folk5"].initial, 7)
        self.assertTrue(isinstance(form.fields[u"folk5"], IntegerField))

        self.assertEquals(form.fields[u"folk6"].initial, None)
        self.assertTrue(isinstance(form.fields[u"folk6"], ChoiceField))
        self.assertEquals(form.fields[u"folk6"].choices, [(True, u"Ja"), (False, u"Nej")])

        self.assertEquals(form.fields[u"folk8"].initial, u"Här är en kommentar")
        self.assertTrue(isinstance(form.fields[u"folk8"], CharField))

        self.assertEquals(form.fields[u"folk35"].initial, 4.77)
        self.assertTrue(isinstance(form.fields[u"folk35"], DecimalField))

        self.assertEquals(form.fields[u"folk52"].initial, 57)
        self.assertTrue(isinstance(form.fields[u"folk52"], IntegerField))

        self.assertEquals(form.fields[u"folk38"].initial, 49130498L)
        self.assertTrue(isinstance(form.fields[u"folk38"], IntegerField))

    def test_form_instance_should_keep_field_order(self):
        form = SurveyObservationsForm(instance=self.survey_response)
        self.assertEquals(form.fields.keys(), [u"folk5", u"folk6", u"folk8", u"folk35", u"folk52", u"folk38"])
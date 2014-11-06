# -*- coding: UTF-8 -*-
from libstat.tests import MongoTestCase

from libstat.models import Survey, Dispatch


class TestSurveyAuthorization(MongoTestCase):

    def test_can_view_survey_if_logged_in(self):
        self._login()
        survey = self._dummy_survey()

        response = self._get("survey", {"survey_id": survey.pk})

        self.assertEquals(response.status_code, 200)
        self.assertTrue("form" in response.context)

    def test_can_view_survey_if_not_logged_in_and_have_correct_password(self):
        survey = self._dummy_survey(password="dummy_password")

        response = self._post(action="survey", kwargs={"survey_id": survey.pk},
                              data={"password": survey.password})

        self.assertEquals(response.status_code, 302)
        response = self._get(action="survey", kwargs={"survey_id": survey.pk})
        self.assertEquals(response.status_code, 200)
        self.assertTrue("form" in response.context)

    def test_can_not_view_survey_if_not_logged_in_and_have_incorrect_password(self):
        survey = self._dummy_survey()

        response = self._get("survey", {"survey_id": survey.pk})

        self.assertEquals(response.status_code, 200)
        self.assertFalse("form" in response.context)

    def test_can_enter_password_if_not_logged_in(self):
        survey = self._dummy_survey()

        response = self._get("survey", {"survey_id": survey.pk})

        self.assertContains(response,
                            u"<button type='submit' class='btn btn-primary'>Visa enkäten</button>",
                            count=1,
                            status_code=200,
                            html=True)

    def test_user_can_still_view_survey_after_leaving_the_page(self):
        survey = self._dummy_survey(password="dummy_password")

        response = self._post(action="survey", kwargs={"survey_id": survey.pk},
                              data={"password": survey.password})

        self.assertEquals(response.status_code, 302)
        response = self._get(action="index")
        self.assertEquals(response.status_code, 200)
        response = self._get(action="survey", kwargs={"survey_id": survey.pk})
        self.assertEquals(response.status_code, 200)
        self.assertTrue("form" in response.context)

    def test_should_not_show_navbar_if_not_logged_in(self):
        survey = self._dummy_survey(password="dummy_password")

        response = self._post(action="survey", kwargs={"survey_id": survey.pk},
                              data={"password": survey.password})
        self.assertEquals(response.status_code, 302)
        response = self._get(action="survey", kwargs={"survey_id": survey.pk})
        self.assertEquals(response.status_code, 200)

        self.assertTrue("hide_navbar" in response.context)
        self.assertNotContains(response,
                               u'<div class="navbar navbar-inverse navbar-static-top" role="navigation">')

    def test_should_show_navbar_if_logged_in(self):
        self._login()
        survey = self._dummy_survey()

        response = self._get(action="survey", kwargs={"survey_id": survey.pk})
        self.assertEquals(response.status_code, 200)

        self.assertFalse("hide_navbar" in response.context)
        self.assertContains(response,
                            u'<div class="navbar navbar-inverse navbar-static-top" role="navigation">')


class TestRemoveSurveys(MongoTestCase):

    def setUp(self):
        self._login()

    def test_removes_selected_surveys(self):
        survey1 = self._dummy_survey()
        survey2 = self._dummy_survey()
        survey3 = self._dummy_survey()
        survey4 = self._dummy_survey()

        response = self._post(action='surveys_remove',
                              data={"survey-response-ids": [survey1.pk, survey3.pk]})

        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(Survey.objects.all()), 2)
        self.assertEquals(len(Survey.objects.filter(pk=survey1.pk)), 0)
        self.assertEquals(len(Survey.objects.filter(pk=survey2.pk)), 1)
        self.assertEquals(len(Survey.objects.filter(pk=survey3.pk)), 0)
        self.assertEquals(len(Survey.objects.filter(pk=survey4.pk)), 1)

    def test_removes_dispatches_linked_to_removed_surveys(self):
        survey1 = self._dummy_survey()
        survey2 = self._dummy_survey()
        survey3 = self._dummy_survey()
        survey4 = self._dummy_survey()
        dispatch1 = Dispatch(survey=survey1).save()
        dispatch2 = Dispatch(survey=survey2).save()
        dispatch3 = Dispatch(survey=survey3).save()
        dispatch4 = Dispatch(survey=survey4).save()

        response = self._post(action='surveys_remove',
                              data={"survey-response-ids": [survey1.pk, survey3.pk]})

        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(Dispatch.objects.all()), 2)
        self.assertEquals(len(Dispatch.objects.filter(pk=dispatch1.pk)), 0)
        self.assertEquals(len(Dispatch.objects.filter(pk=dispatch2.pk)), 1)
        self.assertEquals(len(Dispatch.objects.filter(pk=dispatch3.pk)), 0)
        self.assertEquals(len(Dispatch.objects.filter(pk=dispatch4.pk)), 1)

    def test_can_not_remove_surveys_if_not_logged_in(self):
        self._logout()
        survey1 = self._dummy_survey()
        survey2 = self._dummy_survey()

        response = self._post(action='surveys_remove',
                              data={"survey-response-ids": [survey1.pk, survey2.pk]})

        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(Survey.objects.all()), 2)

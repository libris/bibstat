# -*- coding: UTF-8 -*-
from libstat.tests import MongoTestCase


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

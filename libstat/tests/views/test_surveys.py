# -*- coding: UTF-8 -*-
from libstat.tests import MongoTestCase

from libstat.tests.utils import _login, _get, _post, _dummy_survey


class TestSurveyAuthorization(MongoTestCase):

    def test_can_view_survey_if_logged_in(self):
        _login(self, user="admin", password="admin")
        survey = _dummy_survey()

        response = _get(self, "edit_survey", {"survey_id": survey.pk})

        self.assertEquals(response.status_code, 200)
        self.assertTrue("form" in response.context)

    def test_can_view_survey_if_not_logged_in_and_have_correct_password(self):
        survey = _dummy_survey(password="dummy_password")

        response = _post(self, action="edit_survey", kwargs={"survey_id": survey.pk},
                         data={"password": survey.password})

        self.assertEquals(response.status_code, 302)
        response = _get(self, action="edit_survey", kwargs={"survey_id": survey.pk})
        self.assertEquals(response.status_code, 200)
        self.assertTrue("form" in response.context)

    def test_can_not_view_survey_if_not_logged_in_and_have_incorrect_password(self):
        survey = _dummy_survey()

        response = _get(self, "edit_survey", {"survey_id": survey.pk})

        self.assertEquals(response.status_code, 200)
        self.assertFalse("form" in response.context)

    def test_can_enter_password_if_not_logged_in(self):
        survey = _dummy_survey()

        response = _get(self, "edit_survey", {"survey_id": survey.pk})

        self.assertContains(response,
                            u"<button type='submit' class='btn btn-primary'>Visa enkäten</button>",
                            count=1,
                            status_code=200,
                            html=True)

    def test_user_can_still_view_survey_after_leaving_the_page(self):
        survey = _dummy_survey(password="dummy_password")

        response = _post(self, action="edit_survey", kwargs={"survey_id": survey.pk},
                         data={"password": survey.password})

        self.assertEquals(response.status_code, 302)
        response = _get(self, action="index")
        self.assertEquals(response.status_code, 200)
        response = _get(self, action="edit_survey", kwargs={"survey_id": survey.pk})
        self.assertEquals(response.status_code, 200)
        self.assertTrue("form" in response.context)

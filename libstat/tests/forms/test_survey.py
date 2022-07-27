from libstat.forms.survey import SurveyForm
from libstat.tests import MongoTestCase


class TestUserReadOnly(MongoTestCase):

    def test_form_should_not_be_user_read_only_when_survey_status_is_not_viewed(self):
        survey = self._dummy_survey(status=u"not_viewed")
        form = SurveyForm(survey=survey)

        self.assertFalse(form.is_user_read_only)

    def test_form_should_not_be_user_read_only_when_survey_status_is_initated(self):
        survey = self._dummy_survey(status=u"initiated")
        form = SurveyForm(survey=survey)

        self.assertFalse(form.is_user_read_only)

    def test_form_should_be_user_read_only_when_survey_status_is_submitted(self):
        survey = self._dummy_survey(status=u"submitted")
        form = SurveyForm(survey=survey)

        self.assertTrue(form.is_user_read_only)

    def test_form_should_be_user_read_only_when_survey_status_is_controlled(self):
        survey = self._dummy_survey(status=u"controlled")
        form = SurveyForm(survey=survey)

        self.assertTrue(form.is_user_read_only)

    def test_form_should_be_user_read_only_when_survey_status_is_published(self):
        survey = self._dummy_survey()
        survey.publish()
        form = SurveyForm(survey=survey)

        self.assertTrue(form.is_user_read_only)


class TestReadOnly(MongoTestCase):

    def test_form_should_not_be_read_only_when_authenticated(self):
        survey = self._dummy_survey(status=u"submitted")
        form = SurveyForm(survey=survey, authenticated=True)

        self.assertFalse(form.is_read_only)

    def test_form_should_be_read_only_when_not_authenticated_and_submitted(self):
        survey = self._dummy_survey(status=u"submitted")
        form = SurveyForm(survey=survey, authenticated=False)

        self.assertTrue(form.is_read_only)

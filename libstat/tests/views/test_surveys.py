# -*- coding: UTF-8 -*-

from django.core.urlresolvers import reverse

from libstat.tests import MongoTestCase

from libstat.models import Survey
from libstat.views.surveys import _surveys_as_excel, _dict_to_library, _create_surveys
from libstat.survey_templates import survey_template


class TestSurveyAuthorization(MongoTestCase):

    def test_can_view_survey_if_logged_in(self):
        self._login()
        survey = self._dummy_survey()

        response = self._get("survey", kwargs={"survey_id": survey.pk})

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

        response = self._get("survey", kwargs={"survey_id": survey.pk})

        self.assertEquals(response.status_code, 200)
        self.assertFalse("form" in response.context)

    def test_can_enter_password_if_not_logged_in(self):
        survey = self._dummy_survey()

        response = self._get("survey", kwargs={"survey_id": survey.pk})

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

    def test_can_see_inactive_survey_if_admin(self):
        self._login()
        survey = self._dummy_survey(is_active=False)

        response = self._get(action="survey", kwargs={"survey_id": survey.pk})

        self.assertEquals(response.status_code, 200)

    def test_can_not_see_inactive_survey_if_not_admin(self):
        survey = self._dummy_survey(is_active=False)

        response = self._get(action="survey", kwargs={"survey_id": survey.pk})

        self.assertEquals(response.status_code, 404)


class TestSurveyStatus(MongoTestCase):

    def setUp(self):
        self._login()

    def test_updates_status_for_multiple_surveys(self):
        survey1 = self._dummy_survey(status="not_viewed")
        survey2 = self._dummy_survey(status="initiated")
        survey3 = self._dummy_survey(status="initiated")
        survey4 = self._dummy_survey(status="controlled")

        response = self._post(action='surveys_statuses',
                              data={"survey-response-ids": [survey1.pk, survey3.pk],
                                    "new_status": "controlled"})

        self.assertEquals(response.status_code, 302)
        self.assertEquals(survey1.reload().status, "controlled")
        self.assertEquals(survey2.reload().status, "initiated")
        self.assertEquals(survey3.reload().status, "controlled")
        self.assertEquals(survey4.reload().status, "controlled")


class TestSurveysExport(MongoTestCase):

    def setUp(self):
        self._login()

    def test_can_export_surveys_as_excel(self):
        survey1 = self._dummy_survey()
        survey2 = self._dummy_survey()

        response = self._post(action="surveys_export",
                              data={"survey-response-ids": [survey1.pk, survey2.pk]})

        self.assertEquals(response.status_code, 200)

    def test_sets_correct_values_when_exporting_surveys_as_excel(self):
        survey1 = self._dummy_survey(library=self._dummy_library(name="lib1_name"))
        survey2 = self._dummy_survey(library=self._dummy_library(name="lib2_name"), status="controlled")

        worksheet = _surveys_as_excel([survey1.pk, survey2.pk]).active

        self.assertEquals(worksheet["A1"].value, "Bibliotek")
        self.assertEquals(worksheet["F1"].value, "Kommunkod")
        self.assertEquals(worksheet["A2"].value, "lib1_name")
        self.assertEquals(worksheet["A3"].value, "lib2_name")
        self.assertEquals(worksheet["D3"].value, "Kontrollerad")


class TestLibraryImport(MongoTestCase):

    def setUp(self):
        self._dummy_dict = {
            "country_code": "se",
            "sigel": "lib1_sigel",
            "name": "lib1",
            "library_type": "sjukbib",
            "municipality_code": "1793",
            "address":
            [
                {
                    "address_type": "gen",
                    "city": "lib1_city",
                    "street": "street1"
                },
                {
                    "address_type": "ill",
                    "city": "ill_lib1_city",
                    "street": "ill_street1"
                }
            ],
            "contact":
            [
                {
                    "contact_type": "orgchef",
                    "email": "dont@care.atall"
                },
                {
                    "contact_type": "statans",
                    "email": "lib1@dom.top"
                }
            ]
        }

    def test_creates_library_from_dict(self):
        dict = self._dummy_dict

        library = _dict_to_library(dict)

        self.assertEquals(library.sigel, "lib1_sigel")
        self.assertEquals(library.name, "lib1")
        self.assertEquals(library.city, "lib1_city")
        self.assertEquals(library.address, "street1")
        self.assertEquals(library.email, "lib1@dom.top")
        self.assertEquals(library.municipality_code, "1793")
        self.assertEquals(library.library_type, "sjukbib")

    def test_does_not_import_non_swedish_libraries(self):
        dict = self._dummy_dict
        dict["country_code"] = "dk"

        library = _dict_to_library(dict)

        self.assertEquals(library, None)

    def test_updates_existing_surveys_with_new_library_data(self):
        original_library1 = self._dummy_library(sigel="sigel1", name="old_name1")
        original_library2 = self._dummy_library(sigel="sigel2", name="old_name2")
        survey1 = self._dummy_survey(library=original_library1, sample_year=2014)
        survey2 = self._dummy_survey(library=original_library2, sample_year=2014)

        new_library = self._dummy_library(sigel="sigel1", name="new_name")

        _create_surveys([new_library], 2014)

        survey1.reload()
        survey2.reload()
        self.assertEquals(Survey.objects.count(), 2)
        self.assertEquals(survey1.library.name, "new_name")
        self.assertEquals(survey2.library.name, "old_name2")

    def test_creates_new_surveys_with_new_libraries(self):
        self._dummy_survey(library=self._dummy_library(sigel="sigel1"), sample_year=2013)
        self._dummy_survey(library=self._dummy_library(sigel="sigel2"), sample_year=2013)

        new_library = self._dummy_library(sigel="sigel3")

        _create_surveys([new_library], 2013)

        self.assertEquals(Survey.objects.count(), 3)

    def test_creates_new_surveys_from_2014_template(self):
        library = self._dummy_library(sigel="sigel1")
        self._dummy_variable(key=survey_template(2014).cells[0].variable_key)

        _create_surveys([library], 2014, ignore_missing_variables=True)

        self.assertEquals(len(Survey.objects.all()[0].observations), 1)

    def test_can_create_surveys_for_multiple_years(self):
        library = self._dummy_library(sigel="sigel1")
        self._dummy_variable(key=survey_template(2014).cells[0].variable_key)

        _create_surveys([library], 2014, ignore_missing_variables=True)
        _create_surveys([library], 2015, ignore_missing_variables=True)

        self.assertEquals(Survey.objects.count(), 2)


class TestSurveyView(MongoTestCase):

    def setUp(self):
        self._login()

    def test_should_list_survey_responses_by_year(self):
        self._dummy_survey(sample_year=2012)
        self._dummy_survey(sample_year=2013)

        response = self._get("surveys", params={"action": "list", "sample_year": "2012"})

        self.assertEquals(len(response.context["survey_responses"]), 1)

    def test_should_list_survey_responses_by_target_group(self):
        self._dummy_survey(library=self._dummy_library(library_type="folkbib"), sample_year=2010)
        self._dummy_survey(library=self._dummy_library(library_type="skolbib"), sample_year=2010)
        self._dummy_survey(library=self._dummy_library(library_type="folkbib"), sample_year=2010)

        response = self._get("surveys", params={"action": "list", "target_group": "folkbib", "sample_year": "2010"})

        self.assertEquals(len(response.context["survey_responses"]), 2)

    def test_should_list_survey_responses_by_status(self):
        self._dummy_survey(status="not_viewed", sample_year=2010)
        self._dummy_survey(status="submitted", sample_year=2010)
        self._dummy_survey(status="initiated", sample_year=2010).publish()

        response = self._get("surveys", params={"action": "list", "status": "submitted", "sample_year": "2010"})

        self.assertEquals(len(response.context["survey_responses"]), 1)

    def test_should_list_survey_responses_by_municipality_code(self):
        self._dummy_survey(library=self._dummy_library(municipality_code="1234"))
        self._dummy_survey(library=self._dummy_library(municipality_code="5678"))
        self._dummy_survey(library=self._dummy_library(municipality_code="1234"))

        response = self._get("surveys", params={"action": "list", "municipality_code": "1234"})

        self.assertEquals(len(response.context["survey_responses"]), 2)

    def test_should_list_surveys_when_searching_with_free_text_on_partial_municipality_code(self):
        self._dummy_survey(library=self._dummy_library(municipality_code="1234"))
        self._dummy_survey(library=self._dummy_library(municipality_code="5678"))
        self._dummy_survey(library=self._dummy_library(municipality_code="1234"))

        response = self._get("surveys", params={"action": "list", "free_text": "23"})

        self.assertEquals(len(response.context["survey_responses"]), 2)

    def test_should_list_surveys_when_searching_with_free_text_on_partial_library_name(self):
        self._dummy_survey(library=self._dummy_library(name="abcdef"))
        self._dummy_survey(library=self._dummy_library(name="ghijkl"))
        self._dummy_survey(library=self._dummy_library(name="abcdef"))

        response = self._get("surveys", params={"action": "list", "free_text": "  cde "})

        self.assertEquals(len(response.context["survey_responses"]), 2)

    def test_should_list_surveys_when_searching_with_free_text_on_partial_email(self):
        self._dummy_survey(library=self._dummy_library(name="some@dude.com"))
        self._dummy_survey(library=self._dummy_library(name="another@DuDe.se"))
        self._dummy_survey(library=self._dummy_library(name="third@person.info"))

        response = self._get("surveys", params={"action": "list", "free_text": " @dUdE  "})

        self.assertEquals(len(response.context["survey_responses"]), 2)

    def test_should_list_survey_responses_by_year_and_target_group(self):
        self._dummy_survey(library=self._dummy_library(name="lib1", library_type="folkbib"), sample_year=2012)
        self._dummy_survey(library=self._dummy_library(name="lib2", library_type="folkbib"), sample_year=2013)
        self._dummy_survey(library=self._dummy_library(name="lib3", library_type="skolbib"), sample_year=2013)

        response = self._get("surveys", params={"action": "list", "target_group": "folkbib", "sample_year": "2013"})

        self.assertEquals(len(response.context["survey_responses"]), 1)
        self.assertEquals(response.context["survey_responses"][0].library.name, "lib2")

    def test_each_survey_response_should_have_checkbox_for_actions(self):
        survey = self._dummy_survey(sample_year=2013)

        response = self._get("surveys", params={"action": "list", "sample_year": "2013"})

        self.assertContains(response, 'value="{}"'.format(survey.id))


class TestSurveyState(MongoTestCase):

    def setUp(self):
        self._login()

    def test_returns_active_surveys(self):
        self._dummy_survey(is_active=True, sample_year=2014)
        self._dummy_survey(is_active=False, sample_year=2014)
        self._dummy_survey(is_active=True, sample_year=2014)

        response = self._get("surveys_active", params={"action": "list", "sample_year": "2014"})

        self.assertEquals(len(response.context["survey_responses"]), 2)

    def test_returns_inactive_surveys(self):
        self._dummy_survey(is_active=True, sample_year=2014)
        self._dummy_survey(is_active=False, sample_year=2014)
        self._dummy_survey(is_active=True, sample_year=2014)

        response = self._get("surveys_inactive", params={"action": "list", "sample_year": "2014"})

        self.assertEquals(len(response.context["survey_responses"]), 1)

    def test_can_inactivate_surveys(self):
        survey1 = self._dummy_survey(is_active=True)
        survey2 = self._dummy_survey(is_active=False)
        survey3 = self._dummy_survey(is_active=True)
        self._post("surveys_inactivate", data={"survey-response-ids": [survey1.pk, survey3.pk]})

        survey1.reload()
        survey2.reload()
        survey3.reload()
        self.assertFalse(survey1.is_active)
        self.assertFalse(survey2.is_active)
        self.assertFalse(survey3.is_active)

    def test_can_activate_surveys(self):
        survey1 = self._dummy_survey(is_active=True)
        survey2 = self._dummy_survey(is_active=False)
        survey3 = self._dummy_survey(is_active=False)
        self._post("surveys_activate", data={"survey-response-ids": [survey2.pk]})

        survey1.reload()
        survey2.reload()
        survey3.reload()
        self.assertTrue(survey1.is_active)
        self.assertTrue(survey2.is_active)
        self.assertFalse(survey3.is_active)


class TestSurveysOverview(MongoTestCase):

    def test_can_view_overview_when_logged_in(self):
        self._login()
        self._dummy_survey()

        response = self._get("surveys_overview", kwargs={"sample_year": 2014})

        self.assertEquals(response.status_code, 200)

    def test_can_not_view_overview_when_not_logged_in(self):
        self._dummy_survey()

        response = self._get("surveys_overview", kwargs={"sample_year": 2014})

        self.assertEquals(response.status_code, 302)

# -*- coding: UTF-8 -*-
from datetime import timedelta
from sets import Set
from data.principals import PRINCIPALS

from libstat.tests import MongoTestCase
from libstat.models import OpenData, Survey, SurveyVersion


class TestSurveyModel(MongoTestCase):
    def test_can_not_update_status_to_invalid_value(self):
        survey = self._dummy_survey()

        try:
            survey.status = "some_invalid_status"
            self.assertTrue(False)
        except KeyError:
            pass

    def test_can_create_survey_with_valid_status(self):
        survey = self._dummy_survey(status="not_viewed")

        self.assertEquals(survey.status, "not_viewed")

    def test_can_not_create_survey_with_invalid_status(self):
        try:
            self._dummy_survey(status="some_invalid_status")
            self.assertTrue(False)
        except KeyError:
            pass

    def test_can_update_status_to_valid_value(self):
        survey = self._dummy_survey(status="not_viewed")

        survey.status = "initiated"

        self.assertEquals(survey.status, "initiated")

    def test_should_export_public_non_null_observations_to_openData(self):
        variable = self._dummy_variable(key=u"key1", is_public=True)
        observation = self._dummy_observation(variable=variable, value="val1", _is_public=variable.is_public)
        library = self._dummy_library(name="lib1_name", sigel="lib1_sigel")
        survey = self._dummy_survey(library=library, observations=[observation])

        survey.publish()
        survey.reload()

        open_data = OpenData.objects.all().get(0)
        self.assertEquals(open_data.library_name, "lib1_name")
        self.assertEquals(open_data.variable.key, "key1")
        self.assertEquals(open_data.value, "val1")
        self.assertTrue(open_data.date_modified)
        self.assertTrue(open_data.date_created)
        self.assertEquals(open_data.date_created, open_data.date_modified)
        self.assertEquals(open_data.date_created, survey.published_at)

    def test_should_overwrite_value_and_date_modified_for_existing_openData(self):
        variable = self._dummy_variable(key=u"key1", is_public=True)
        observation = self._dummy_observation(variable=variable, value="old_value", _is_public=variable.is_public)
        library = self._dummy_library(name="lib1_name", sigel="lib1_sigel", library_type="folkbib")
        survey = self._dummy_survey(library=library, observations=[observation])

        survey.publish()
        survey.reload()

        for obs in survey.observations:
            if obs.variable.key == "key1":
                obs.value = "new_value"
        survey.save()
        survey.publish()

        data = OpenData.objects.all()
        self.assertEquals(len(data), 1)

        open_data = data.get(0)
        self.assertEquals(open_data.library_name, "lib1_name")
        self.assertEquals(open_data.target_group, "folkbib")
        self.assertEquals(open_data.value, "new_value")
        self.assertTrue(open_data.date_modified)
        self.assertTrue(open_data.date_created)
        self.assertNotEquals(open_data.date_created, open_data.date_modified)

    def test_should_get_observation_by_variable_key(self):
        observation1 = self._dummy_observation(variable=self._dummy_variable(key="key1"))
        observation2 = self._dummy_observation(variable=self._dummy_variable(key="key2"))
        observation3 = self._dummy_observation(variable=self._dummy_variable(key="key3"))
        survey = self._dummy_survey(observations=[
            observation1,
            observation2,
            observation3
        ])
        self.assertEquals(survey.observation_by_key("key2"), observation2)

    def test_should_store_version_when_updating_existing_object(self):
        library = self._dummy_library(name="lib1_old_name", city="lib1_old_city", sigel="lib1_sigel")
        survey = self._dummy_survey(status="initiated", library=library)

        survey.library.name = "lib1_new_name"
        survey.library.city = "lib1_new_city"
        survey.status = "controlled"
        survey = survey.save()

        self.assertEquals(survey.library.name, "lib1_new_name")
        self.assertEquals(survey.library.city, "lib1_new_city")
        self.assertEquals(survey.status, "controlled")

        versions = SurveyVersion.objects.filter(survey_response_id=survey.id)
        self.assertEquals(len(versions), 1)
        self.assertEquals(versions[0].survey_response_id, survey.id)
        self.assertEquals(versions[0].library.name, "lib1_old_name")
        self.assertEquals(versions[0].library.city, "lib1_old_city")
        self.assertEquals(versions[0].status, "initiated")

    def test_should_store_one_version_for_each_change(self):
        survey = self._dummy_survey()
        self.assertEquals(len(SurveyVersion.objects.all()), 0)

        survey.library.name = "new_name"
        survey.save()
        self.assertEquals(len(SurveyVersion.objects.all()), 1)

        survey.library.name = "newer_name"
        survey.save()
        self.assertEquals(len(SurveyVersion.objects.all()), 2)

    def test_should_store_version_when_updating_observations_for_existing_objects(self):
        survey = self._dummy_survey(observations=[
            self._dummy_observation(variable=self._dummy_variable(key="key1"))
        ])
        self.assertEquals(len(SurveyVersion.objects.all()), 0)

        survey.observation_by_key("key1").value = "new_value"
        survey.save()

        self.assertEquals(len(SurveyVersion.objects.all()), 1)

    def test_should_not_store_version_when_creating_object(self):
        library = self._dummy_library()
        survey = self._dummy_survey(library=library)

        versions = SurveyVersion.objects.filter(survey_response_id=survey.id)
        self.assertEquals(len(versions), 0)

    def test_should_set_modified_date_when_updating_existing_object(self):
        survey = self._dummy_survey()
        survey.library.name = "new_name"
        survey.save().reload()

        self.assertTrue(survey.date_modified > survey.date_created)

    def test_should_not_set_modified_date_when_updating_notes_in_existing_object(self):
        survey = self._dummy_survey()
        survey.notes = "new_notes"
        survey.save().reload()

        self.assertEquals(survey.date_modified, survey.date_created)

    def test_should_not_store_version_when_updating_notes_in_existing_object(self):
        survey = self._dummy_survey()
        self.assertEquals(len(SurveyVersion.objects.filter(survey_response_id=survey.id)), 0)

        survey.notes = "new_notes"
        survey.save()

        self.assertEquals(len(SurveyVersion.objects.filter(survey_response_id=survey.id)), 0)

    def test_should_flag_as_not_published_when_updating_existing_object(self):
        survey = self._dummy_survey()
        survey.library.name = "new_name"
        survey.save().reload()

        self.assertFalse(survey.is_published)

    def test_should_not_flag_as_not_published_when_updating_notes_in_existing_object(self):
        survey = self._dummy_survey()
        survey.publish()
        self.assertTrue(survey.is_published)

        survey.notes = "new_notes"
        survey.save()

        self.assertTrue(survey.is_published)

    def test_should_set_modified_date_when_creating_object(self):
        survey = self._dummy_survey()

        self.assertEquals(survey.date_modified, survey.date_created)


class TestSurveyPublish(MongoTestCase):
    def test_returns_true_if_publish_successful(self):
        survey = self._dummy_survey()

        successful = survey.publish()

        self.assertTrue(successful)

    def test_returns_false_if_not_publish_successful(self):
        survey = self._dummy_survey(selected_libraries=[])

        successful = survey.publish()

        self.assertFalse(successful)

    def test_should_flag_new_object_as_not_published(self):
        survey = self._dummy_survey()

        self.assertFalse(survey.is_published)

    def test_should_set_published_date_but_not_modified_date_when_publishing(self):
        survey = self._dummy_survey()
        date_modified = survey.date_modified

        survey.publish()

        self.assertNotEquals(survey.published_at, None)
        self.assertEquals(survey.date_modified, date_modified)

    def test_should_flag_as_published_when_publishing(self):
        survey = self._dummy_survey()

        survey.publish()
        survey.reload()

        self.assertTrue(survey.is_published)

    def test_latest_version_published(self):
        library = self._dummy_library()
        survey = self._dummy_survey(library=library)

        survey.published_at = survey.date_modified + timedelta(hours=-1)
        self.assertFalse(survey.latest_version_published)

        survey.published_at = survey.date_modified
        self.assertTrue(survey.latest_version_published)

        survey.published_at = None
        self.assertFalse(survey.latest_version_published)

        survey.status = "submitted"
        self.assertFalse(survey.latest_version_published)

        survey.publish()
        self.assertTrue(survey.latest_version_published)

    def test_is_published(self):
        survey = self._dummy_survey()
        self.assertFalse(survey.is_published)

        survey.publish()
        self.assertTrue(survey.is_published)

    def test_creates_open_data_when_publishing(self):
        survey = self._dummy_survey(observations=[
            self._dummy_observation(),
            self._dummy_observation()])
        self.assertEquals(len(OpenData.objects.all()), 0)

        survey.publish()
        self.assertEquals(len(OpenData.objects.all()), 2)

    def test_does_not_create_new_open_data_for_existing_open_data_when_republishing(self):
        survey = self._dummy_survey(observations=[
            self._dummy_observation(value="old_value")])
        survey.publish()

        self.assertEquals(len(OpenData.objects.all()), 1)

        survey.observations[0].value = "new_value"
        survey.publish()

        self.assertEquals(len(OpenData.objects.all()), 1)

    def test_modifies_existing_open_data_that_has_changed_when_republishing(self):
        survey = self._dummy_survey(observations=[
            self._dummy_observation(value="old_value")])
        survey.publish()

        self.assertEquals(OpenData.objects.all()[0].value, "old_value")

        survey.observations[0].value = "new_value"
        survey.publish()

        self.assertEquals(OpenData.objects.all()[0].value, "new_value")

    def test_updates_date_modified_for_open_data_that_has_changed_when_republishing(self):
        survey = self._dummy_survey(observations=[
            self._dummy_observation(value="old_value")])
        survey.publish()

        self.assertEquals(OpenData.objects.all()[0].date_modified, OpenData.objects.all()[0].date_created)

        survey.observations[0].value = "new_value"
        survey.publish()

        self.assertTrue(OpenData.objects.all()[0].date_modified > OpenData.objects.all()[0].date_created)

    def test_does_not_update_date_modified_for_open_data_that_has_not_changed_when_republishing(self):
        variable1 = self._dummy_variable(key="key1")
        variable2 = self._dummy_variable(key="key2")
        survey = self._dummy_survey(observations=[
            self._dummy_observation(variable1, value="old_value1"),
            self._dummy_observation(variable2, value="old_value2")])
        survey.publish()

        self.assertEquals(OpenData.objects.filter(variable=variable2)[0].date_modified,
                          OpenData.objects.filter(variable=variable2)[0].date_created)

        survey.observation_by_key("key1").value = "new_value1"
        survey.publish()

        self.assertEquals(OpenData.objects.filter(variable=variable2)[0].date_modified,
                          OpenData.objects.filter(variable=variable2)[0].date_created)

    def test_does_not_modify_existing_open_data_that_has_not_changed_when_republishing(self):
        variable1 = self._dummy_variable(key="key1")
        variable2 = self._dummy_variable(key="key2")
        survey = self._dummy_survey(observations=[
            self._dummy_observation(variable1, value="old_value1"),
            self._dummy_observation(variable2, value="old_value2")])
        survey.publish()

        self.assertEquals(OpenData.objects.filter(variable=variable2)[0].value, "old_value2")

        survey.observation_by_key("key1").value = "new_value1"
        survey.publish()

        self.assertEquals(OpenData.objects.filter(variable=variable2)[0].value, "old_value2")

    def test_sets_existing_open_data_as_inactive_when_revoking_publication(self):
        survey = self._dummy_survey(observations=[self._dummy_observation()])
        survey.publish()

        self.assertTrue(OpenData.objects.all()[0].is_active)

        survey.unpublish()

        self.assertFalse(OpenData.objects.all()[0].is_active)

    def test_sets_existing_open_data_as_active_when_publishing_after_revoking_publication(self):
        survey = self._dummy_survey(observations=[self._dummy_observation()])
        survey.publish()

        self.assertEquals(len(OpenData.objects.all()), 1)
        self.assertTrue(OpenData.objects.all()[0].is_active)

        survey.unpublish()

        self.assertEquals(len(OpenData.objects.all()), 1)
        self.assertFalse(OpenData.objects.all()[0].is_active)

        survey.publish()

        self.assertEquals(len(OpenData.objects.all()), 1)
        self.assertTrue(OpenData.objects.all()[0].is_active)

    def test_revokes_publication_when_changing_status_from_published(self):
        survey = self._dummy_survey(observations=[self._dummy_observation()])
        survey.publish()

        self.assertTrue(survey.is_published)
        self.assertTrue(OpenData.objects.all()[0].is_active)

        survey.status = "submitted"

        self.assertFalse(survey.is_published)
        self.assertFalse(OpenData.objects.all()[0].is_active)

    def test_can_not_publish_survey_if_it_has_no_selected_libraries(self):
        survey = self._dummy_survey(selected_libraries=[])

        survey.publish()
        survey.save()
        survey.reload()

        self.assertFalse(survey.is_published)

    def test_does_not_create_open_data_when_publishing_survey_if_it_has_no_selected_libraries(self):
        survey = self._dummy_survey(selected_libraries=[],
                                    observations=[
                                        self._dummy_observation(),
                                        self._dummy_observation(),
                                    ])

        survey.publish()

        self.assertEquals(OpenData.objects.count(), 0)

    def test_can_not_publish_survey_if_another_survey_reports_for_the_same_library(self):
        self._dummy_library(sigel="lib1")
        self._dummy_library(sigel="lib2")
        self._dummy_library(sigel="lib3")

        survey1 = self._dummy_survey(selected_libraries=["lib1", "lib3"])
        survey2 = self._dummy_survey(selected_libraries=["lib2", "lib3"])

        survey1.publish()
        survey2.publish()

        self.assertFalse(survey1.is_published)
        self.assertFalse(survey2.is_published)


class TestSelectableLibraries(MongoTestCase):
    def test_should_return_an_empty_list_for_no_municipality_code(self):
        survey = self._dummy_survey(library=self._dummy_library(municipality_code=None))

        self.assertItemsEqual(survey.selectable_libraries(), [])

    def test_should_exclude_second_library_with_different_municipality_code(self):
        survey = self._dummy_survey(library=self._dummy_library(municipality_code="1"))
        self._dummy_survey(library=self._dummy_library(municipality_code="2"))

        self.assertItemsEqual(survey.selectable_libraries(), [])

    def test_should_include_second_library_with_same_municipality_code(self):
        library = self._dummy_library(municipality_code="1")
        second = self._dummy_library(municipality_code="1")
        survey = self._dummy_survey(library=library)
        self._dummy_survey(library=second)
        selectables = survey.selectable_libraries()

        self.assertEqual(len(selectables), 1)
        self.assertEqual(selectables[0], second)

    def test_should_exclude_second_library_with_same_sigel(self):
        survey = self._dummy_survey(library=self._dummy_library(sigel="1"))
        self._dummy_survey(library=self._dummy_library(sigel="1"))

        self.assertItemsEqual(survey.selectable_libraries(), [])

    def test_should_include_second_library_with_same_municipality_code_and_same_principal_library_type(self):
        library = self._dummy_library(municipality_code="1", library_type=u"folkbib")
        second = self._dummy_library(municipality_code="1", library_type=u"muskom")
        survey = self._dummy_survey(library=library)
        self._dummy_survey(library=second)
        selectables = survey.selectable_libraries()

        self.assertEqual(len(selectables), 1)
        self.assertEqual(selectables[0], second)

    def test_should_exclude_second_library_with_same_municipality_code_and_different_principal_library_type(self):
        library = self._dummy_library(municipality_code="1", library_type=u"folkbib")
        second = self._dummy_library(municipality_code="1", library_type=u"sjukbib")
        survey = self._dummy_survey(library=library)
        self._dummy_survey(library=second)
        selectables = survey.selectable_libraries()

        self.assertEqual(len(selectables), 0)

    def test_should_include_second_library_with_same_municipality_code_when_library_type_is_unknown(self):
        library = self._dummy_library(municipality_code="1", library_type=None)
        second = self._dummy_library(municipality_code="1", library_type=u"muskom")
        survey = self._dummy_survey(library=library)
        self._dummy_survey(library=second)
        selectables = survey.selectable_libraries()

        self.assertEqual(len(selectables), 1)
        self.assertEqual(selectables[0], second)

    def test_should_include_second_library_with_same_municipality_code_when_principal_is_unknown_for_library_type(self):
        library = self._dummy_library(municipality_code="1", library_type=u"musbib")
        self.assertFalse(library.library_type in PRINCIPALS)

        second = self._dummy_library(municipality_code="1", library_type=u"muskom")
        survey = self._dummy_survey(library=library)
        self._dummy_survey(library=second)
        selectables = survey.selectable_libraries()

        self.assertEqual(len(selectables), 1)
        self.assertEqual(selectables[0], second)


class TestSelectedSigels(MongoTestCase):
    def test_should_return_an_empty_set_for_no_municipality_code(self):
        library = self._dummy_library(municipality_code=None)
        survey = self._dummy_survey(sample_year=2014)

        self.assertSetEqual(survey.selected_sigels(2014), Set())

    def test_should_include_second_surveys_selected_sigel(self):
        library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")

        survey = self._dummy_survey(library=library, sample_year=2014)
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["2"])

        self.assertSetEqual(survey.selected_sigels(2014), {"2"})

    def test_should_include_librarys_own_sigel_when_selected_in_second_survey(self):
        library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")

        survey = self._dummy_survey(library=library, sample_year=2014)
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["1", "2"])

        self.assertSetEqual(survey.selected_sigels(2014), {"1", "2"})

    def test_should_exclude_selected_sigel_for_another_sample_year(self):
        library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")

        survey = self._dummy_survey(library=library, sample_year=2014)
        self._dummy_survey(library=second_library, sample_year=2015, selected_libraries=["1", "2"])

        self.assertSetEqual(survey.selected_sigels(2014), Set())

    def test_should_exclude_selected_sigel_for_another_municipality_code(self):
        library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2", municipality_code="m")

        survey = self._dummy_survey(library=library, sample_year=2014)
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["2"])

        self.assertSetEqual(survey.selected_sigels(2014), Set())

    def test_should_exclude_selected_sigel_in_librarys_own_survey(self):
        library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")

        survey = self._dummy_survey(library=library, sample_year=2014, selected_libraries=["3"])
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["2"])

        self.assertSetEqual(survey.selected_sigels(2014), {"2"})

    def test_should_include_second_surveys_selected_sigel_with_same_principal_library_type(self):
        library = self._dummy_library(sigel="1", library_type=u"folkbib")
        second_library = self._dummy_library(sigel="2", library_type=u"muskom")

        survey = self._dummy_survey(library=library, sample_year=2014)
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["2"])

        self.assertSetEqual(survey.selected_sigels(2014), {"2"})

    def test_should_exclude_second_surveys_selected_sigel_with_different_principal_library_type(self):
        library = self._dummy_library(sigel="1", library_type=u"folkbib")
        second_library = self._dummy_library(sigel="2", library_type=u"sjukbib")

        survey = self._dummy_survey(library=library, sample_year=2014)
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["2"])

        self.assertSetEqual(survey.selected_sigels(2014), Set())

    def test_should_include_second_surveys_selected_sigel_when_library_type_is_unknown(self):
        library = self._dummy_library(sigel="1", library_type=None)
        second_library = self._dummy_library(sigel="2", library_type=u"muskom")

        survey = self._dummy_survey(library=library, sample_year=2014)
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["2"])

        self.assertSetEqual(survey.selected_sigels(2014), {"2"})

    def test_should_include_second_surveys_selected_sigel_when_principal_is_unknown_for_library_type(self):
        library = self._dummy_library(sigel="1", library_type=u"musbib")
        self.assertFalse(library.library_type in PRINCIPALS)
        second_library = self._dummy_library(sigel="2", library_type=u"muskom")

        survey = self._dummy_survey(library=library, sample_year=2014)
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["2"])

        self.assertSetEqual(survey.selected_sigels(2014), {"2"})


class TestHasConflicts(MongoTestCase):
    def test_should_return_true_for_conflict_in_same_sample_year(self):
        first_library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")

        survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=["1", "2"])
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["2"])

        self.assertTrue(survey.has_conflicts())

    def test_should_return_false_for_non_conflict_in_different_sample_years(self):
        first_library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")

        survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=["1", "2"])
        self._dummy_survey(library=second_library, sample_year=2015, selected_libraries=["2"])

        self.assertFalse(survey.has_conflicts())

    def test_should_return_false_for_non_conflict_in_same_sample_year(self):
        first_library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")

        survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=["1"])
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["2"])

        self.assertFalse(survey.has_conflicts())

    def test_should_return_true_for_conflict_when_second_survey_reports_for_first_survey(self):
        first_library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")

        survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=[])
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["1", "2"])

        self.assertTrue(survey.has_conflicts())

    def test_should_return_true_for_conflict_when_second_survey_reports_for_first_survey_with_same_principal_library_type(
            self):
        first_library = self._dummy_library(sigel="1", library_type=u"folkbib")
        second_library = self._dummy_library(sigel="2", library_type=u"muskom")

        survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=[])
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["1", "2"])

        self.assertTrue(survey.has_conflicts())

    def test_should_return_false_for_non_conflict_when_second_survey_reports_for_first_survey_with_different_principal_library_type(
            self):
        first_library = self._dummy_library(sigel="1", library_type=u"folkbib")
        second_library = self._dummy_library(sigel="2", library_type=u"sjukbib")

        survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=[])
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["1", "2"])

        self.assertFalse(survey.has_conflicts())

    def test_should_return_true_for_conflict_when_second_survey_reports_for_first_survey_when_library_type_is_unknown(
            self):
        first_library = self._dummy_library(sigel="1", library_type=None)
        second_library = self._dummy_library(sigel="2", library_type=u"muskom")

        survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=[])
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["1", "2"])

        self.assertTrue(survey.has_conflicts())

    def test_should_return_true_for_conflict_when_second_survey_reports_for_first_survey_when_principal_for_library_type_is_unknown(
            self):
        first_library = self._dummy_library(sigel="1", library_type=u"musbib")
        self.assertFalse(first_library.library_type in PRINCIPALS)
        second_library = self._dummy_library(sigel="2", library_type=u"muskom")

        survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=[])
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["1", "2"])

        self.assertTrue(survey.has_conflicts())


class TestGetConflictingSurveys(MongoTestCase):
    def test_should_return_survey_for_conflict_in_same_sample_year(self):
        first_library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="3")

        first_survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=["1", "2"])
        second_survey = self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["2"])

        self.assertListEqual(first_survey.get_conflicting_surveys(), [second_survey])

    def test_should_return_two_surveys_for_conflicts_in_same_sample_year(self):
        first_library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")
        third_library = self._dummy_library(sigel="3")

        first_survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=["1", "2"])
        second_survey = self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["1"])
        third_survey = self._dummy_survey(library=third_library, sample_year=2014, selected_libraries=["2"])

        self.assertListEqual(first_survey.get_conflicting_surveys(), [second_survey, third_survey])

    def test_should_return_empty_list_for_non_conflict_in_different_sample_years(self):
        first_library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="3")

        first_survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=["1", "2"])
        self._dummy_survey(library=second_library, sample_year=2015, selected_libraries=["2"])

        self.assertListEqual(first_survey.get_conflicting_surveys(), [])

    def test_should_return_second_survey_when_reporting_for_first_survey(self):
        first_library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")

        first_survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=[])
        second_survey = self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["1", "2"])

        self.assertListEqual(first_survey.get_conflicting_surveys(), [second_survey])

    def test_should_return_second_survey_when_reporting_for_first_survey_with_same_principal_library_type(self):
        first_library = self._dummy_library(sigel="1", library_type=u"folkbib")
        second_library = self._dummy_library(sigel="2", library_type=u"muskom")

        first_survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=[])
        second_survey = self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["1", "2"])

        self.assertListEqual(first_survey.get_conflicting_surveys(), [second_survey])

    def test_should_not_return_second_survey_when_reporting_for_first_survey_with_different_principal_library_type(
            self):
        first_library = self._dummy_library(sigel="1", library_type=u"folkbib")
        second_library = self._dummy_library(sigel="2", library_type=u"sjukbib")

        first_survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=[])
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["1", "2"])

        self.assertListEqual(first_survey.get_conflicting_surveys(), [])

    def test_should_return_second_survey_when_reporting_for_first_survey_when_library_type_is_unknown(self):
        first_library = self._dummy_library(sigel="1", library_type=None)
        second_library = self._dummy_library(sigel="2", library_type=u"sjukbib")

        first_survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=[])
        second_survey = self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["1", "2"])

        self.assertListEqual(first_survey.get_conflicting_surveys(), [second_survey])

    def test_should_return_second_survey_when_reporting_for_first_survey_when_principal_for_library_type_is_unknown(
            self):
        first_library = self._dummy_library(sigel="1", library_type=u"musbib")
        self.assertFalse(first_library.library_type in PRINCIPALS)
        second_library = self._dummy_library(sigel="2", library_type=u"sjukbib")

        first_survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=[])
        second_survey = self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["1", "2"])

        self.assertListEqual(first_survey.get_conflicting_surveys(), [second_survey])


class TestPreviousYearsSurvey(MongoTestCase):
    def test_finds_survey_from_previous_year_if_identical_names_ignoring_case(self):
        previous_years_survey = self._dummy_survey(sample_year=2013,
                                                   library=self._dummy_library(u"ALLINGSÅS BIBLIOTEK"))
        this_years_survey = self._dummy_survey(sample_year=2014,
                                               library=self._dummy_library(u"Allingsås bibliotek"))

        self.assertEqual(previous_years_survey, this_years_survey.previous_years_survey())

    def test_does_not_find_survey_from_previous_year_if_not_identical_names_ignoring_case(self):
        self._dummy_survey(sample_year=2013,
                           library=self._dummy_library(u"BOTKYRKA BIBLIOTEK"))
        this_years_survey = self._dummy_survey(sample_year=2014,
                                               library=self._dummy_library(u"Allingsås bibliotek"))

        self.assertEqual(None, this_years_survey.previous_years_survey())
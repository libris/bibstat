# -*- coding: UTF-8 -*-
from sets import Set

from libstat.forms.survey import SurveyForm, LibrarySelection
from libstat.tests import MongoTestCase


class TestLibrarySelection_SelectableLibraries(MongoTestCase):
    def test_should_return_an_empty_list_for_no_municipality_code(self):
        library = self._dummy_library(municipality_code=None)
        selection = LibrarySelection(library)
        self._dummy_library()

        self.assertItemsEqual(selection.selectable_libraries(), [])


    def test_should_exclude_second_library_with_different_municipality_code(self):
        library = self._dummy_library(municipality_code="1")
        self._dummy_library(municipality_code="2")
        selection = LibrarySelection(library)

        self.assertItemsEqual(selection.selectable_libraries(), [])


    def test_should_include_second_library_with_same_municipality_code(self):
        library = self._dummy_library(municipality_code="1")
        second = self._dummy_library(municipality_code="1")
        selection = LibrarySelection(library)

        self.assertItemsEqual(selection.selectable_libraries(), [second])


    def test_should_exclude_second_library_with_same_sigel(self):
        library = self._dummy_library(sigel="1")
        self._dummy_library(sigel="1")
        selection = LibrarySelection(library)

        self.assertItemsEqual(selection.selectable_libraries(), [])

class TestLibrarySelection_SelectedSigels(MongoTestCase):
    def test_should_return_an_empty_set_for_no_municipality_code(self):
        library = self._dummy_library(municipality_code=None)
        selection = LibrarySelection(library)
        self._dummy_survey(sample_year=2014)

        self.assertSetEqual(selection.selected_sigels(2014), Set())

    def test_should_include_second_surveys_selected_sigel(self):
        library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")

        self._dummy_survey(library=library, sample_year=2014)
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["2"])
        selection = LibrarySelection(library)

        self.assertSetEqual(selection.selected_sigels(2014), {"2"})

    def test_should_exclude_librarys_own_sigel_when_selected_in_second_survey(self):
        library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")

        self._dummy_survey(library=library, sample_year=2014)
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["1", "2"])
        selection = LibrarySelection(library)

        self.assertSetEqual(selection.selected_sigels(2014), {"2"})

    def test_should_exclude_selected_sigel_for_another_sample_year(self):
        library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")

        self._dummy_survey(library=library, sample_year=2014)
        self._dummy_survey(library=second_library, sample_year=2015, selected_libraries=["1", "2"])
        selection = LibrarySelection(library)

        self.assertSetEqual(selection.selected_sigels(2014), Set())

    def test_should_exclude_selected_sigel_for_another_municipality_code(self):
        library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2", municipality_code="m")

        self._dummy_survey(library=library, sample_year=2014)
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["2"])
        selection = LibrarySelection(library)

        self.assertSetEqual(selection.selected_sigels(2014), Set())

    def test_should_exclude_selected_sigel_in_librarys_own_survey(self):
        library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")

        self._dummy_survey(library=library, sample_year=2014, selected_libraries=["3"])
        self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["2"])
        selection = LibrarySelection(library)

        self.assertSetEqual(selection.selected_sigels(2014), {"2"})

class TestLibrarySelection_HasConflicts(MongoTestCase):
    def test_should_return_true_for_conflict_in_same_sample_year(self):
        first_library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")

        first_survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=["1", "2"])
        second_survey = self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["2"])

        selection = LibrarySelection(first_library)
        self.assertTrue(selection.has_conflicts(first_survey))


    def test_should_return_false_for_non_conflict_in_different_sample_years(self):
        first_library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")

        first_survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=["1", "2"])
        second_survey = self._dummy_survey(library=second_library, sample_year=2015, selected_libraries=["2"])

        selection = LibrarySelection(first_library)
        self.assertFalse(selection.has_conflicts(first_survey))

    def test_should_return_false_for_non_conflict_in_same_sample_year(self):
        first_library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")

        first_survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=["1"])
        second_survey = self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["2"])

        selection = LibrarySelection(first_library)
        self.assertFalse(selection.has_conflicts(first_survey))

class TestLibrarySelection_GetConflictingSurveys(MongoTestCase):
    def test_should_return_survey_for_conflict_in_same_sample_year(self):
        first_library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="3")

        first_survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=["1", "2"])
        second_survey = self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["2"])

        conflicts = LibrarySelection(first_library).get_conflicting_surveys(first_survey)
        self.assertListEqual(conflicts, [second_survey])

    def test_should_return_two_surveys_for_conflicts_in_same_sample_year(self):
        first_library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="2")
        third_library = self._dummy_library(sigel="3")

        first_survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=["1", "2"])
        second_survey = self._dummy_survey(library=second_library, sample_year=2014, selected_libraries=["1"])
        third_survey = self._dummy_survey(library=third_library, sample_year=2014, selected_libraries=["2"])

        conflicts = LibrarySelection(first_library).get_conflicting_surveys(first_survey)
        self.assertListEqual(conflicts, [second_survey, third_survey])

    def test_should_return_empty_list_for_non_conflict_in_different_sample_years(self):
        first_library = self._dummy_library(sigel="1")
        second_library = self._dummy_library(sigel="3")

        first_survey = self._dummy_survey(library=first_library, sample_year=2014, selected_libraries=["1", "2"])
        second_survey = self._dummy_survey(library=second_library, sample_year=2015, selected_libraries=["2"])

        conflicts = LibrarySelection(first_library).get_conflicting_surveys(first_survey)
        self.assertListEqual(conflicts, [])

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


# coding=utf-8
from sets import Set
from django import forms
from django.core.urlresolvers import reverse
from bibstat import settings
from data.principals import get_library_types_with_same_principal
from libstat.models import Survey, Variable, SurveyObservation
from libstat.survey_templates import survey_template


class LibrarySelection:

    def __init__(self, library):
        self.library = library

    def selectable_libraries(self):
        if not self.library.municipality_code:
            return []

        return [survey.library for survey in Survey.objects.filter(
            library__municipality_code=self.library.municipality_code,
            library__library_type__in=get_library_types_with_same_principal(self.library),
            library__sigel__ne=self.library.sigel
        )]

    def selected_sigels(self, sample_year):
        if not self.library.municipality_code:
            return Set()

        surveys = Survey.objects.filter(
            sample_year=sample_year,
            library__municipality_code=self.library.municipality_code,
            library__library_type__in=get_library_types_with_same_principal(self.library),
            library__sigel__ne=self.library.sigel
        )

        selected_sigels = Set()
        for survey in surveys:
            for sigel in survey.selected_libraries:
                selected_sigels.add(sigel)

        return selected_sigels

    def has_conflicts(self, survey):
        for selected_sigel in self.selected_sigels(survey.sample_year):
            if selected_sigel in survey.selected_libraries or selected_sigel == self.library.sigel:
                return True

        return False

    def get_conflicting_surveys(self, survey):
        if not self.library.municipality_code:
            return []

        other_surveys = Survey.objects.filter(
            sample_year=survey.sample_year,
            library__municipality_code=self.library.municipality_code,
            library__library_type__in=get_library_types_with_same_principal(self.library),
            library__sigel__ne=self.library.sigel
        )

        return [
            other_survey for other_survey in other_surveys
            if any(sigel in other_survey.selected_libraries for sigel in survey.selected_libraries)
            or self.library.sigel in other_survey.selected_libraries
        ]


class SurveyForm(forms.Form):

    def _cell_to_input_field(self, cell, observation):
        attrs = {"class": "form-control",
                 "id": cell.variable_key,
                 "name": cell.variable_key}

        if cell.sum_of:
            attrs["data-sum-of"] = " ".join(map(lambda s: s, cell.sum_of))
            attrs["data-bv-notempty"] = ""
            attrs["placeholder"] = "Obligatorisk"

        if "required" in cell.types:
            attrs["data-bv-notempty"] = ""
            attrs["placeholder"] = "Obligatorisk"

        if "integer" in cell.types:
            attrs["data-bv-integer"] = ""
            attrs["data-bv-greaterthan"] = ""
            attrs["data-bv-greaterthan-value"] = "0"
            attrs["data-bv-greaterthan-inclusive"] = ""

        if "numeric" in cell.types:
            attrs["data-bv-numeric"] = ""
            attrs["data-bv-numeric-separator"] = "."
            attrs["data-bv-greaterthan"] = ""
            attrs["data-bv-greaterthan-value"] = "0"
            attrs["data-bv-greaterthan-inclusive"] = ""
        if "text" in cell.types:
            attrs["data-bv-stringlength"] = ""
            attrs["data-bv-stringlength-min"] = "0"

        if observation.disabled:
            attrs["disabled"] = ""

        if "comment" in cell.types:
            field = forms.CharField(required=False, widget=forms.Textarea(attrs=attrs))
        elif "integer" in cell.types:
            field = forms.IntegerField(required=False, widget=forms.TextInput(attrs=attrs))
        elif "numeric" in cell.types:
            field = forms.FloatField(required=False, widget=forms.TextInput(attrs=attrs))
        else:
            field = forms.CharField(required=False, widget=forms.TextInput(attrs=attrs))

        field.initial = u"Värdet är okänt" if observation.value_unknown else observation.value

        return field

    def _set_libraries(self, current_library, this_surveys_selected_sigels, authenticated):
        selection = LibrarySelection(current_library)
        other_surveys_selected_sigels = selection.selected_sigels(self.sample_year)

        def set_library(self, library, current_library=False):
            checkbox_id = str(library.sigel)

            attrs = {
                "value": checkbox_id,
                "class": "select-library"
            }

            row = {
                "name": library.name,
                "city": library.city,
                "address": library.address,
                "sigel": library.sigel,
                "checkbox_id": checkbox_id
            }

            if self.is_read_only:
                attrs["disabled"] = "true"

            if library.sigel in other_surveys_selected_sigels:
                attrs["disabled"] = "true"
                row["comment"] = u"Detta bibliotek rapporteras redan för i en annan enkät."
                if current_library or library.sigel in this_surveys_selected_sigels:
                    row["comment"] = u"Rapporteringen för detta bibliotek kolliderar med en annan enkät."
                    self.library_selection_conflict = True
                    del attrs["disabled"]

            if current_library:
                attrs["disabled"] = "true"
                if not authenticated or library.sigel in this_surveys_selected_sigels:
                    attrs["checked"] = "true"

                if not library.sigel in other_surveys_selected_sigels:
                    row["comment"] = u"Detta är det bibliotek som enkäten avser i första hand."
            elif library.sigel in this_surveys_selected_sigels:
                attrs["checked"] = "true"

            if authenticated:
                try:
                    del attrs["disabled"]
                except KeyError:
                    pass

            self.fields[checkbox_id] = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs=attrs))
            self.libraries.append(row)

        self.libraries = []
        set_library(self, current_library, current_library=True)
        for library in selection.selectable_libraries():
            set_library(self, library)

    def _status_label(self, key):
        return next((status[1] for status in Survey.STATUSES if status[0] == key))

    def _conflicting_libraries(self, first_selection, second_selection):
        intersection = Set(first_selection).intersection(Set(second_selection))
        return [survey.library for survey in Survey.objects.filter(library__sigel__in=intersection)]

    def __init__(self, *args, **kwargs):
        survey = kwargs.pop('survey', None)
        authenticated = kwargs.pop('authenticated', False)
        super(SurveyForm, self).__init__(*args, **kwargs)

        template = survey_template(survey.sample_year, survey)

        self.fields["disabled_inputs"] = forms.CharField(
            required=False, widget=forms.HiddenInput(attrs={"id": "disabled_inputs"}))
        self.fields["unknown_inputs"] = forms.CharField(
            required=False, widget=forms.HiddenInput(attrs={"id": "unknown_inputs"}))
        self.fields["selected_libraries"] = forms.CharField(
            required=False, widget=forms.HiddenInput(attrs={"id": "selected_libraries"}))
        self.fields["submit_action"] = forms.CharField(
            required=False, widget=forms.HiddenInput(attrs={"id": "submit_action"}))
        self.fields["read_only"] = forms.CharField(required=False, widget=forms.HiddenInput(attrs={"id": "read_only"}))
        self.fields["key"] = forms.CharField(required=False, widget=forms.HiddenInput(), initial=survey.pk)
        self.fields["selected_status"] = forms.CharField(
            required=False, widget=forms.HiddenInput(), initial=survey.status)

        intro_variable = Variable.objects.filter(key=template.intro_text_variable_key)
        self.intro_text = intro_variable[0].description if intro_variable.count() != 0 else ""
        self.library_name = survey.library.name
        self.library_sigel = survey.library.sigel
        self.city = survey.library.city
        self.municipality_code = survey.library.municipality_code
        self.sample_year = survey.sample_year
        self.is_user_read_only = not survey.status in (u"not_viewed", u"initiated")
        self.is_read_only = not authenticated and self.is_user_read_only
        self.can_submit = not authenticated and survey.status in ("not_viewed", "initiated")
        self.password = survey.password
        self.status = self._status_label(survey.status)
        self.notes = survey.notes if survey.notes else ""
        self.notes_rows = min(max(5, survey.notes.count('\n') if survey.notes else 0) + 1, 10)
        self.statuses = Survey.STATUSES
        self.is_published = survey.status == "published"
        self.latest_version_published = survey.latest_version_published
        self.sections = template.sections

        self.url = settings.API_BASE_URL + reverse('survey', args=(survey.pk,))
        self.url_with_password = "{}?p={}".format(self.url, self.password)

        self._set_libraries(survey.library, survey.selected_libraries, authenticated)
        if hasattr(self, 'library_selection_conflict') and self.library_selection_conflict:
            selection = LibrarySelection(survey.library)

            self.conflicting_surveys = selection.get_conflicting_surveys(survey)
            for conflicting_survey in self.conflicting_surveys:
                conflicting_survey.url = settings.API_BASE_URL + reverse('survey', args=(conflicting_survey.pk,))
                conflicting_survey.conflicting_libraries = self._conflicting_libraries(
                    survey.selected_libraries + [survey.library.sigel],
                    conflicting_survey.selected_libraries)

            self.can_submit = False

        variables = {}
        for variable in Variable.objects.all():
            variables[variable.key] = variable

        for cell in template.cells:
            variable_key = cell.variable_key
            if not variable_key in variables:
                raise Exception("Can't find variable with key '{}'".format(variable_key))
            observation = survey.get_observation(variable_key)

            cell.disabled = observation.disabled
            if not observation:
                survey.observations.append(SurveyObservation(variable=variables[variable_key]))
            self.fields[variable_key] = self._cell_to_input_field(cell, observation)

        if self.is_read_only:
            self.fields["read_only"].initial = "true"
            for key, input in self.fields.iteritems():
                input.widget.attrs["readonly"] = ""

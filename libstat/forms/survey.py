import logging
import time
import json

from django import forms
from django.urls import reverse

from bibstat import settings
from data.municipalities import municipalities
from libstat.models import Survey, Variable, SurveyObservation
from libstat.survey_templates import survey_template

logger = logging.getLogger(__name__)

class SurveyForm(forms.Form):

    def _cell_to_input_field(self, cell, observation, authenticated, variable_type):
        attrs = {"class": "form-control",
                 "id": cell.variable_key,
                 "name": cell.variable_key}

        if cell.sum_of:
            attrs["data-sum-of"] = " ".join(map(lambda s: s, cell.sum_of))
            attrs["data-bv-notempty"] = ""
            attrs["placeholder"] = "Obligatorisk"

        if cell.part_of:
            attrs["data-bv-callback"] = ""
            if isinstance(cell.part_of, list):
                part_of_as_string = " ".join(cell.part_of)
                attrs["data-part-of"] = part_of_as_string
                attrs["data-bv-callback-message"] = u"Värdet får inte vara högre än värdet i följande fält: {}".format(part_of_as_string)
            else:
                attrs["data-part-of"] = cell.part_of
                attrs["data-bv-callback-message"] = u"Värdet får inte vara högre än värdet i fältet {}".format(cell.part_of)

        if cell.has_part:
            attrs["data-bv-callback"] = ""
            if isinstance(cell.has_part, list):
                has_part_as_string = " ".join(cell.has_part)
                attrs["data-has-part"] = has_part_as_string
                if not cell.part_of:
                    attrs["data-bv-callback-message"] = u"Värdet får inte vara mindre än värdet i följande fält: {}".format(has_part_as_string)
            else:
                attrs["data-has-part"] = cell.has_part
                if not cell.part_of:
                    attrs["data-bv-callback-message"] = u"Värdet får inte vara mindre än värdet i fältet {}".format(cell.has_part)

        if cell.required == True:
            attrs["data-bv-notempty"] = ""
            attrs["placeholder"] = "Obligatorisk"
            attrs["aria-required"] = "true"

        if variable_type in ["integer", "decimal"]:
            # Numerical fields need special treatment with JS because of
            # thousands separators. The class "numerical" is how they can be
            # selected.
            attrs["class"] = "{} numerical".format(attrs["class"])
            if cell.previous_value is not None and cell.previous_value != '':
                attrs["data-previous-value"] = cell.previous_value
            else:
                attrs["data-previous-value"] = 'null'

        if "Namn" in cell.variable_key:
            attrs["autocomplete"] = "name"

        if "Plan" in cell.variable_key:
            attrs["type"] = "url"
            attrs["autocomplete"] = "url"

        # Utgifter and Intakter max 999 999 999 or 999 999 999,999
        if "Utgift" in cell.variable_key or "Intakt" in cell.variable_key:
            attrs["data-bv-regexp"] = ""
            if variable_type == "integer":
                attrs["data-bv-regexp-regexp"] = "^(-|(0|[1-9 ]([0-9 ]){0,10}))$"
                attrs["data-bv-regexp-message"] = u"Vänligen mata in ett numeriskt värde mindre än eller lika med 999 999 999, alternativt '-' om värdet inte är relevant"
            elif variable_type == "decimal":
                attrs["data-bv-regexp-regexp"] = "^(-|[\d ]{1,11}(\,[\d ]{1,3})?)$"
                attrs["data-bv-regexp-message"] = u"Vänligen mata in ett numeriskt värde mindre än eller lika med 999 999 999,999 med max 3 decimaler (t ex 12,522), alternativt '-' om värdet inte är relevant"

        else:

            # Integer max value is 99 999 999
            if variable_type == "integer":
                attrs["data-bv-regexp"] = ""
                attrs["data-bv-regexp-regexp"] = "^(-|(0|[1-9 ]([0-9 ]){0,9}))$"
                attrs["data-bv-message"] = u"Vänligen mata in ett numeriskt värde mindre än eller lika med 99 999 999, alternativt '-' om värdet inte är relevant"

            # Decimal max value is 99 999 999,999
            if variable_type == "decimal":
                attrs["data-bv-regexp"] = ""
                attrs["data-bv-regexp-regexp"] = "^(-|[\d ]{1,10}(\,[\d ]{1,3})?)$"
                attrs["data-bv-regexp-message"] = u"Vänligen mata in ett numeriskt värde mindre än eller lika med 99999999,999 med max 3 decimaler (t ex 12,522), alternativt '-' om värdet inte är relevant"

            if variable_type == "email":
                #attrs["data-bv-emailaddress"] = ""
                attrs["data-bv-regexp"] = ""
                attrs["autocomplete"] = "email"
                attrs["type"] = "email"
                attrs["data-bv-regexp-regexp"] = "^([\w!#$%&'*+/=?`{|}~^-]+(?:\.[\w!#$%&'*+/=?`{|}~^-]+)*@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,6})$"
                attrs["data-bv-regexp-message"] = u"Vänligen mata in en giltig emailadress"

            if variable_type == "string":
                attrs["data-bv-stringlength"] = ""
                attrs["data-bv-stringlength-min"] = "0"

            if variable_type == "phonenumber":
                attrs["data-bv-regexp"] = ""
                attrs["autocomplete"] = "tel"
                attrs["type"] = "tel"
                attrs["data-bv-regexp-regexp"] = "^(-|\+?(\d\d?-?)+\d(\s?\d+)*\d+)$"
                attrs["data-bv-regexp-message"] = u"Vänligen mata in ett giltigt telefonnummer utan bokstäver och parenteser, t ex 010-709 30 00"

        # Number of hours per week
        if "Open103" in cell.variable_key:
            attrs["data-bv-between"] = "true"
            attrs["data-bv-between-min"] = "0"
            attrs["data-bv-between-max"] = "168"

        # Number of days per year
        if "Open101" in cell.variable_key:            
            attrs["data-bv-between"] = "true"
            attrs["data-bv-between-min"] = "0"
            attrs["data-bv-between-max"] = "366"

        if not observation or observation.value_unknown:
            attrs["disabled"] = ""
            attrs["class"] = "{} value-unknown".format(attrs["class"])

            attrs["data-original-value"] = observation.value if observation and observation.value is not None else ""

        if authenticated:
            attrs["class"] = "{} survey-popover".format(attrs["class"])
            attrs["data-toggle"] = "tooltip"
            attrs["data-placement"] = "top"
            attrs["data-original-title"] = cell.variable_key

        # Note: all fields are CharFields and types are casted before saving the form
        if variable_type == "textarea":
            field = forms.CharField(required=False, widget=forms.Textarea(attrs=attrs))
        else:
            field = forms.CharField(required=False, widget=forms.TextInput(attrs=attrs))

        if not observation or observation.value_unknown:
            field.initial = u"Värdet är okänt"
        elif observation.value != None and variable_type == "decimal":
            field.initial = str(observation.value).replace(".", ",") # decimals are displayed with comma in the form
        else:
            field.initial = observation.value

        if isinstance(field.initial, str):
            field.initial = field.initial.strip()

        if cell.variable_key == "Besok01":
            logger.debug("attrs:")
            for attr, value in attrs.items():
                logger.debug(attr)

        return field

    def _set_libraries(self, current_survey, this_surveys_selected_sigels, authenticated):
        other_surveys_selected_sigels = current_survey.selected_sigels_in_other_surveys(self.sample_year)

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
                attrs["disabled"] = "disabled"

            if library.sigel in other_surveys_selected_sigels:
                attrs["disabled"] = "disabled"
                row["comment"] = u"Detta bibliotek rapporteras redan för i en annan enkät."
                if current_library or library.sigel in this_surveys_selected_sigels:
                    row["comment"] = u"Rapporteringen för detta bibliotek kolliderar med en annan enkät."
                    self.library_selection_conflict = True
                    del attrs["disabled"]

            if current_library:
                attrs["disabled"] = "disabled"
                if not authenticated or library.sigel in this_surveys_selected_sigels:
                    attrs["checked"] = "checked"

                if not library.sigel in other_surveys_selected_sigels:
                    row["comment"] = u"Detta är det bibliotek som mottagit denna enkät. Om du samredovisar med andra bibliotek, glöm inte att även kryssa för dem här i listan."
            elif library.sigel in this_surveys_selected_sigels:
                attrs["checked"] = "checked"

            if authenticated:
                try:
                    del attrs["disabled"]
                except KeyError:
                    pass

            self.fields[checkbox_id] = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs=attrs))
            self.libraries.append(row)

        self.libraries = []
        set_library(self, current_survey.library, current_library=True)

        for library in current_survey.selectable_libraries():
            set_library(self, library)

    def _status_label(self, key):
        return next((status[1] for status in Survey.STATUSES if status[0] == key))

    def _conflicting_libraries(self, first_selection, second_selection):
        intersection = set(first_selection).intersection(set(second_selection))
        survey_list = []
        sigel_list = []
        for survey in Survey.objects.filter(library__sigel__in=intersection):
            if survey.library.sigel not in sigel_list:
                survey_list.append(survey.library)
                sigel_list.append(survey.library.sigel)
        return survey_list

    def _mailto_link(self):
        body = (
            u"%0D%0A"
            u"----------" + "%0D%0A"
            u"Var%20vänlig%20och%20låt%20följande%20information%20stå%20kvar%20i%20meddelandet." + "%0D%0A"
            u"" + "%0D%0A"
            u"Bibliotek:%20{}%20({})%20i%20{}".format(self.library_name, self.library_sigel, self.city) + "%0D%0A"
            u"Kommun/län:%20{}%20({})".format(municipalities.get(self.municipality_code, ""), self.municipality_code) + "%0D%0A"
            u"Statistikansvarig:%20{}".format(self.email) + "%0D%0A"
            u"Insamlingsår:%20{}".format(self.sample_year) + "%0D%0A"
            u"----------"
        )

        return (
            u"mailto:biblioteksstatistik@kb.se"
            u"?subject=Fråga%20för%20statistikenkät:%20{}%20({})".format(self.library_name, self.library_sigel) +
            u"&body={}".format(body)
        )

    def __init__(self, *args, **kwargs):
        survey = kwargs.pop('survey', None)
        authenticated = kwargs.pop('authenticated', False)
        super(SurveyForm, self).__init__(*args, **kwargs)

        # Cache variables for performance
        variables = {}
        for variable in Variable.objects.all():
            variables[variable.key] = variable

        template = survey_template(survey.sample_year, survey)

        self.fields["disabled_inputs"] = forms.CharField(
            required=False, widget=forms.HiddenInput(attrs={"id": "disabled_inputs"})) #TODO: remove?
        self.fields["unknown_inputs"] = forms.CharField(
            required=False, widget=forms.HiddenInput(attrs={"id": "unknown_inputs"}))
        self.fields["altered_fields"] = forms.CharField(
            required=False, widget=forms.HiddenInput(attrs={"id": "altered_fields"}))
        self.fields["selected_libraries"] = forms.CharField(
            required=False, widget=forms.HiddenInput(attrs={"id": "selected_libraries"}))
        self.fields["scroll_position"] = forms.CharField(
            required=False, widget=forms.HiddenInput(attrs={"id": "scroll_position"}))
        self.fields["submit_action"] = forms.CharField(
            required=False, widget=forms.HiddenInput(attrs={"id": "submit_action"}))
        self.fields["read_only"] = forms.CharField(required=False, widget=forms.HiddenInput(attrs={"id": "read_only"}))
        self.fields["key"] = forms.CharField(required=False, widget=forms.HiddenInput(), initial=survey.pk)
        self.fields["selected_status"] = forms.CharField(
            required=False, widget=forms.HiddenInput(), initial=survey.status)

        intro_text = variables[template.intro_text_variable_key].description if template.intro_text_variable_key in variables else ""
        self.intro_text = intro_text
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

        self.url = settings.API_BASE_URL + reverse('survey', args=(survey.pk,))
        self.url_with_password = "{}?p={}".format(self.url, self.password)
        self.email = survey.library.email
        self.mailto = self._mailto_link()

        self._set_libraries(survey, survey.selected_libraries, authenticated)

        if hasattr(self, 'library_selection_conflict') and self.library_selection_conflict:
            self.conflicting_surveys = survey.get_conflicting_surveys()
            for conflicting_survey in self.conflicting_surveys:
                conflicting_survey.url = settings.API_BASE_URL + reverse('survey', args=(conflicting_survey.pk,))
                conflicting_survey.conflicting_libraries = self._conflicting_libraries(
                    survey.selected_libraries + [survey.library.sigel],
                    conflicting_survey.selected_libraries)

            self.can_submit = False

        previous_survey = survey.previous_years_survey()

        for cell in template.cells:
            variable_key = cell.variable_key
            if not variable_key in variables:
                raise Exception("Can't find variable with key '{}'".format(variable_key))
            variable_type = variables[variable_key].type
            cell.types.append(variable_type) #cell is given same type as variable
            observation = survey.get_observation(variable_key)

            if observation:
                cell.disabled = observation.disabled #TODO: remove?
                cell.value_unknown = observation.value_unknown
                if previous_survey:
                    cell.previous_value = survey.previous_years_value(observation.variable, previous_survey)
            if not observation:
                observation = SurveyObservation(variable=variables[variable_key])
                survey.observations.append(observation)
            self.fields[variable_key] = self._cell_to_input_field(cell, observation, authenticated, variable_type)

        self.sections = template.sections

        if self.is_read_only:
            self.fields["read_only"].initial = "true"
            for key, input in self.fields.items():
                input.widget.attrs["readonly"] = ""

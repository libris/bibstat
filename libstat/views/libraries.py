# -*- coding: UTF-8 -*-
import requests
import random
import string

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required

from libstat.models import Library, LibrarySelection, Survey, SurveyObservation, Variable
from libstat.forms import CreateSurveysForm
from libstat.survey_templates import survey_template


# From: http://en.wikipedia.org/wiki/Random_password_generator#Python
def _generate_password():
    alphabet = string.letters[0:52] + string.digits
    return str().join(random.SystemRandom().choice(alphabet) for _ in range(10))


def _create_surveys(library_ids, sample_year):
    for library_id in library_ids:
        library = Library.objects.get(pk=library_id)
        template = survey_template(sample_year)
        survey = Survey(
            library_name=library.name,
            library=library,
            sample_year=sample_year,
            target_group="public",
            password=_generate_password(),
            observations=[])
        for section in template.sections:
            for group in section.groups:
                for row in group.rows:
                    for cell in row.cells:
                        survey.observations.append(
                            SurveyObservation(
                                variable=Variable.objects.get(key=cell.variable_key)))
        survey.save()


@permission_required('is_superuser', login_url='index')
def libraries(request):
    if request.method == "POST":
        form = CreateSurveysForm(request.POST)
        if form.is_valid():
            sample_year = int(form.cleaned_data.pop("sample_year"))
            library_ids = []
            for field in form.cleaned_data:
                if form.cleaned_data[field]:
                    library_ids.append(field)
        if "create_surveys_btn" in form.data:
            _create_surveys(library_ids, sample_year)
            return redirect(reverse("surveys"))
        elif "save_selection_btn" in form.data:
            lib_selection, _ = LibrarySelection.objects.get_or_create(name="lib_selection")
            lib_selection.sigels = []
            for lib_id in library_ids:
                lib_selection.sigels.append(Library.objects.get(pk=lib_id).sigel)
            lib_selection.save()

    return render(request, 'libstat/libraries.html', {"form": CreateSurveysForm()})


def _dict_to_library(dict):
    if not dict["country_code"] == "se":
        return None

    library, _ = Library.objects.get_or_create(sigel=dict["sigel"])
    library.sigel = dict["sigel"]
    library.name = dict["name"]
    library.city = next((a["city"] for a in dict["address"]
                         if a["address_type"] == "gen"), None)
    library.email = next((c["email"] for c in dict["contact"]
                          if "email" in c and c["contact_type"] == "statans"), None)

    return library


def _update_libraries():
    for start_index in range(0, 6000, 200):  # bibdb paginated by 200 and had ca. 2800 responses when this was written
        response = requests.get(
            url="http://bibdb.libris.kb.se/api/lib?dump=true&start=%d" % start_index,
            headers={"APIKEY_AUTH_HEADER": "bibstataccess"})

        for lib_data in response.json()["libraries"]:
            library = _dict_to_library(lib_data)
            if library:
                library.save()


@permission_required('is_superuser', login_url='index')
def remove_libraries(request):
    Library.objects.all().delete()
    return redirect(reverse('libraries'))


@permission_required('is_superuser', login_url='index')
def import_libraries(request):
    _update_libraries()
    return redirect(reverse('libraries'))

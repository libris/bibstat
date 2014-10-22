import requests

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required

from libstat.models import Library, SurveyResponse, SurveyObservation, Variable
from libstat.forms import CreateSurveysForm
from libstat.survey_templates import survey_template


def _create_surveys(library_ids, sample_year):
    for library_id in library_ids:
        library = Library.objects.get(pk=library_id)
        template = survey_template(sample_year)
        survey = SurveyResponse(
            library_name=library.name,
            library=library,
            sample_year=sample_year,
            target_group="public",
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
            _create_surveys(library_ids, sample_year)
            return redirect(reverse("survey_responses"))

    return render(request,
                  'libstat/libraries.html',
                  {
                      "form": CreateSurveysForm()
                  })


def _update_libraries():
    for start_index in range(0, 6000, 200):
        response = requests.get(
            url="http://bibdb.libris.kb.se/api/lib?dump=true&start=%d" % start_index,
            headers={"APIKEY_AUTH_HEADER": "bibstataccess"})
        for lib_data in response.json()["libraries"]:
            try:
                library = Library.objects.get(sigel=lib_data["sigel"])
            except Library.DoesNotExist:
                library = Library()
            library.sigel = lib_data["sigel"]
            library.name = lib_data["name"]
            library.municipality_name = next((a["city"] for a in lib_data["address"] if a["address_type"] == "gen"),
                                             "")
            # library.email = "a@a.a"  # next((c["email"] for c in lib_data["contact"]
            # if c["contact_type"] == "bibchef"), "dummy@dummy.org")
            library.save()


@permission_required('is_superuser', login_url='index')
def remove_libraries(request):
    Library.objects.filter().delete()
    return redirect(reverse('libraries'))


@permission_required('is_superuser', login_url='index')
def import_libraries(request):
    _update_libraries()
    return redirect(reverse('libraries'))

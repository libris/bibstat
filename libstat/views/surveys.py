# -*- coding: utf-8 -*-
import logging
import requests
from time import strftime

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from bibstat import settings
from libstat import utils
from libstat.models import Survey, Library, SurveyObservation, Variable
from libstat.survey_templates import has_template, survey_template


logger = logging.getLogger(__name__)


@permission_required('is_superuser', login_url='index')
def surveys(request, *args, **kwargs):
    surveys_state = kwargs.pop("surveys_state", "active")

    sample_years = Survey.objects.distinct("sample_year")
    sample_years.sort()
    sample_years.reverse()

    municipality_codes = Survey.objects.distinct("library.municipality_code")
    municipality_codes.sort()

    target_group = request.GET.get("target_group", "")
    sample_year = request.GET.get("sample_year", str(sample_years[0]) if sample_years else "")
    municipality_code = request.GET.get("municipality_code", "")
    status = request.GET.get("status", "")
    message = request.session.pop("message", "")
    free_text = request.GET.get("free_text", "").strip()

    surveys = []
    if not sample_year:
        message = u"Du måste ange för vilket år du vill lista enkätsvar."
    else:
        surveys = Survey.objects.by(
            sample_year=sample_year,
            target_group=target_group,
            status=status,
            municipality_code=municipality_code,
            free_text=free_text,
            is_active=surveys_state == "active")

    context = {
        'current_url': request.get_full_path,
        'sample_year': sample_year,
        'sample_years': sample_years,
        'municipality_code': municipality_code,
        'municipality_codes': municipality_codes,
        'target_group': target_group,
        'target_groups': utils.SURVEY_TARGET_GROUPS,
        'status': status,
        'statuses': Survey.STATUSES,
        'free_text': free_text,
        'surveys_state': surveys_state,
        'num_active_surveys': Survey.objects.filter(is_active=True, sample_year=sample_year).count(),
        'num_inactive_surveys': Survey.objects.filter(is_active=False, sample_year=sample_year).count(),
        'survey_responses': surveys,
        'message': message,
        'url_base': settings.API_BASE_URL,
        'bibdb_library_base_url': u"{}/library".format(settings.BIBDB_BASE_URL),
        'nav_surveys_css': 'active'
    }

    return render(request, 'libstat/surveys.html', context)


@permission_required('is_superuser', login_url='index')
def surveys_active(request):
    return surveys(request, surveys_state="active")


@permission_required('is_superuser', login_url='index')
def surveys_inactive(request):
    return surveys(request, surveys_state="inactive")


@permission_required('is_superuser', login_url='index')
def surveys_activate(request):
    if request.method == "POST":
        survey_ids = request.POST.getlist("survey-response-ids", [])
        for survey in Survey.objects.filter(pk__in=survey_ids):
            survey.is_active = True
            survey.save()
        request.session["message"] = "Aktiverade {} st enkäter.".format(len(survey_ids))
        return surveys(request, surveys_state="active")


@permission_required('is_superuser', login_url='index')
def surveys_inactivate(request):
    if request.method == "POST":
        survey_ids = request.POST.getlist("survey-response-ids", [])
        for survey in Survey.objects.filter(pk__in=survey_ids):
            survey.is_active = False
            survey.save()
        request.session["message"] = "Inaktiverade {} st enkäter.".format(len(survey_ids))
        return surveys(request, surveys_state="inactive")


def _surveys_redirect(request):
    if request.method == "GET":
        method = request.GET
    elif request.method == "POST":
        method = request.POST
    target_group = method.get("target_group", "")
    sample_year = method.get("sample_year", "")
    status = method.get("status", "")
    return HttpResponseRedirect(u"{}{}".format(
        reverse("surveys"),
        u"?action=list&target_group={}&sample_year={}&status={}".format(target_group, sample_year, status)))


def _surveys_as_excel(survey_ids):
    def variable_keys_in(survey):
        variable_keys = []
        if has_template(survey.sample_year):
            template = survey_template(survey.sample_year)
            for cell in template.cells:
                variable_keys.append(cell.variable_key)
        else:
            for observation in surveys[0].observations:
                variable_keys.append(unicode(observation.variable.key))
        return variable_keys

    surveys = Survey.objects.filter(id__in=survey_ids).order_by('library__name')

    variable_keys = variable_keys_in(surveys[0])

    headers = [
        "Bibliotek",
        "Sigel",
        "Bibliotekstyp",
        "Status",
        "Email",
        "Kommunkod",
        "Stad",
        "Adress",
        "Huvudman",
    ] + variable_keys

    workbook = Workbook(encoding="utf-8")
    worksheet = workbook.active
    worksheet.append(headers)

    for survey in surveys:
        row = [
            survey.library.name,
            survey.library.sigel,
            survey.library.library_type,
            Survey.status_label(survey.status),
            survey.library.email,
            survey.library.municipality_code,
            survey.library.city,
            survey.library.address,
            survey.principal,

        ]
        for key in variable_keys:
            row.append(survey.get_observation(key).value)
        worksheet.append(row)

    return workbook


@permission_required('is_superuser', login_url='index')
def surveys_export(request):
    if request.method == "POST":
        survey_ids = request.POST.getlist("survey-response-ids", [])
        filename = u"Exporterade enkätsvar ({}).xlsx".format(strftime("%Y-%m-%d %H.%M.%S"))
        workbook = _surveys_as_excel(survey_ids)

        response = HttpResponse(save_virtual_workbook(workbook), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = u'attachment; filename="{}"'.format(filename)
        return response


@permission_required('is_superuser', login_url='index')
def surveys_overview(request, sample_year):
    surveys = Survey.objects.filter(sample_year=sample_year)
    context = {
        "sample_year": sample_year,
        "statuses": Survey.STATUSES,
        "library_types": utils.SURVEY_TARGET_GROUPS,
        "surveys": surveys
    }

    return render(request, "libstat/surveys_overview.html", context)


@permission_required('is_superuser', login_url='index')
def surveys_statuses(request):
    status = request.POST.get("new_status", "")
    survey_response_ids = request.POST.getlist("survey-response-ids", [])
    for survey in Survey.objects.filter(id__in=survey_response_ids):
        survey.status = status
        survey.save()
    message = u"Ändrade status på {} enkäter.".format(len(survey_response_ids))

    request.session["message"] = message
    return _surveys_redirect(request)


def _create_surveys(libraries, sample_year):
    template_cells = survey_template(sample_year).cells

    variables = {}  # Fetch variables once for IO-performance
    for variable in Variable.objects.all():
        variables[variable.key] = variable

    existing_surveys = {}
    for survey in Survey.objects.all():
        existing_surveys[(survey.library.sigel, survey.sample_year)] = survey

    created = 0
    for library in libraries:
        if (library.sigel, sample_year) in existing_surveys:
            survey = existing_surveys[(library.sigel, sample_year)]
            survey.library = library
        else:
            survey = Survey(
                library=library,
                sample_year=sample_year,
                observations=[])
            for cell in template_cells:
                variable_key = cell.variable_key
                if not variable_key in variables:
                    raise Exception("Can't find variable with key '{}'".format(variable_key))
                survey.observations.append(SurveyObservation(variable=variables[variable_key]))
            created += 1

        survey.save()

    return created


def _dict_to_library(dict):
    if not dict["country_code"] == "se":
        return None

    library = Library()
    library.sigel = dict.get("sigel") if dict.get("sigel") else None
    library.name = dict.get("name") if dict.get("name") else None
    library.municipality_code = dict.get("municipality_code") if dict.get("municipality_code") else None
    library.library_type = dict.get("library_type") if dict.get("library_type") else None
    location = next((a for a in dict["address"] if a["address_type"] == "gen"), None)
    library.address = location["street"] if location and location["street"] else None
    library.city = location["city"] if location and location["city"] else None
    library.email = next((c["email"] for c in dict["contact"]
                          if "email" in c and c["contact_type"] == "statans"), None)

    return library


def _get_libraries_from_bibdb():
    libraries = []
    # bibdb api paginated by 200 and had ca. 2800 responses when this was written
    for start_index in range(0, 6000, 200):
        response = requests.get(
            url="http://bibdb.libris.kb.se/api/lib?dump=true&start=%d" % start_index,
            headers={"APIKEY_AUTH_HEADER": "bibstataccess"})

        for lib_data in response.json()["libraries"]:
            library = _dict_to_library(lib_data)
            if library:
                libraries.append(library)
    return libraries


def _create_new_collection(year):
    libraries = _get_libraries_from_bibdb()
    _create_surveys(libraries, year)


@permission_required('is_superuser', login_url='index')
def import_and_create(request):
    sample_year = request.POST.get("sample_year")
    sample_year = int(sample_year)
    _create_new_collection(sample_year)
    return redirect(reverse('surveys'))

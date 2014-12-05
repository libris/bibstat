# -*- coding: utf-8 -*-
import logging
from bson import ObjectId
from mongoengine.context_managers import no_dereference
import requests
from time import strftime

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from bibstat import settings
from data.principals import principal_for_library_type
from libstat import utils
from libstat.models import Survey, Library, SurveyObservation, Variable
from libstat.survey_templates import has_template, survey_template
from data.municipalities import municipalities

logger = logging.getLogger(__name__)


@permission_required('is_superuser', login_url='index')
def surveys(request, *args, **kwargs):
    sample_years = Survey.objects.distinct("sample_year")
    sample_years.sort()
    sample_years.reverse()

    municipality_codes = Survey.objects.distinct("library.municipality_code")
    municipality_codes = [(municipalities[code], code) for code in municipality_codes if code in municipalities]
    municipality_codes.sort()

    target_group = request.GET.get("target_group", "")
    sample_year = request.GET.get("sample_year", str(sample_years[0]) if sample_years else "")
    municipality_code = request.GET.get("municipality_code", "")
    status = request.GET.get("status", "")
    message = request.session.pop("message", "")
    free_text = request.GET.get("free_text", "").strip()
    surveys_state = request.GET.get("surveys_state", "active")

    surveys = []
    active_surveys = []
    inactive_surveys = []
    if Survey.objects.count() == 0:
        message = u"Det finns inga enkäter inlagda i systemet."
    elif not sample_year:
        message = u"Du måste ange för vilket år du vill lista enkätsvar."
    else:
        active_surveys = Survey.objects.by(
            sample_year=sample_year,
            target_group=target_group,
            status=status,
            municipality_code=municipality_code,
            free_text=free_text,
            is_active=True)
        inactive_surveys = Survey.objects.by(
            sample_year=sample_year,
            target_group=target_group,
            status=status,
            municipality_code=municipality_code,
            free_text=free_text,
            is_active=False)
        surveys = active_surveys if surveys_state == "active" else inactive_surveys
        surveys = surveys.order_by("library.name")

    # Triggering lazy loading of the list of surveys before iterating over it in the
    # template seems to give significant performance gains. Unknown why.
    surveys = list(surveys)

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
        'survey_responses': surveys,
        'message': message,
        'survey_base_url': reverse("surveys"),
        'url_base': settings.API_BASE_URL,
        'bibdb_library_base_url': u"{}/library".format(settings.BIBDB_BASE_URL),
        'nav_surveys_css': 'active',
        'num_active_surveys': active_surveys.count() if active_surveys else 0,
        'num_inactive_surveys': inactive_surveys.count() if inactive_surveys else 0
    }

    return render(request, 'libstat/surveys.html', context)


@permission_required('is_superuser', login_url='index')
def surveys_activate(request):
    if request.method == "POST":
        survey_ids = request.POST.getlist("survey-response-ids", [])
        Survey.objects.filter(pk__in=survey_ids).update(set__is_active=True)
        request.session["message"] = "Aktiverade {} stycken enkäter.".format(len(survey_ids))
        return redirect("{}?surveys_state=inactive".format(reverse("surveys")))


@permission_required('is_superuser', login_url='index')
def surveys_inactivate(request):
    if request.method == "POST":
        survey_ids = request.POST.getlist("survey-response-ids", [])
        Survey.objects.filter(pk__in=survey_ids).update(set__is_active=False)
        request.session["message"] = "Inaktiverade {} stycken enkäter.".format(len(survey_ids))
        return redirect("{}?surveys_state=active".format(reverse("surveys")))


def _surveys_redirect(request):
    if request.method == "GET":
        method = request.GET
    elif request.method == "POST":
        method = request.POST

    target_group = method.get("target_group", "")
    sample_year = method.get("sample_year", "")
    status = method.get("status", "")
    free_text = method.get("free_text", "")
    return HttpResponseRedirect(u"{}{}".format(
        reverse("surveys"),
        u"?action=list&target_group={}&sample_year={}&status={}&free_text={}".format(target_group, sample_year, status, free_text)))


def _surveys_as_excel(survey_ids):
    surveys = Survey.objects.filter(id__in=survey_ids).order_by('library__name')
    variable_keys = [unicode(observation.variable.key) for observation in surveys[0].observations]

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
                  "Kan publiceras?"
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
            principal_for_library_type[survey.library.library_type]
            if survey.library.library_type in principal_for_library_type else None,
            "Ja" if survey.can_publish() else "Nej: " + survey.reasons_for_not_able_to_publish()
        ]
        for observation in survey.observations:
            row.append(observation.value)
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
    table = [[""]]
    for status in Survey.STATUSES:
        table[0].append(status[1])
    table[0].append("Total")

    for library_type in utils.SURVEY_TARGET_GROUPS:
        row = [library_type[1]]
        for status in Survey.STATUSES:
            row.append(Survey.objects.filter(is_active=True, sample_year=sample_year, _status=status[0],
                                             library__library_type=library_type[0]).count())
        row.append(Survey.objects.filter(is_active=True, sample_year=sample_year,
                                         library__library_type=library_type[0]).count())
        table.append(row)

    row = ["Total"]
    for status in Survey.STATUSES:
        row.append(Survey.objects.filter(is_active=True, sample_year=sample_year, _status=status[0]).count())
    row.append(Survey.objects.filter(is_active=True, sample_year=sample_year).count())
    table.append(row)

    context = {
        "sample_year": sample_year,
        "table": table
    }

    return render(request, "libstat/surveys_overview.html", context)


@permission_required('is_superuser', login_url='index')
def surveys_statuses(request):
    status = request.POST.get("new_status", "")
    survey_response_ids = request.POST.getlist("survey-response-ids", [])
    if status == "published":
        num_successful_published = 0
        for survey in Survey.objects.filter(id__in=survey_response_ids):
            successful = survey.publish()
            if successful:
                num_successful_published += 1
        message = u"Publicerade {} stycken enkäter.".format(num_successful_published)
        if num_successful_published != len(survey_response_ids):
            message = (u"{} Kunde inte publicera {} enkäter eftersom de inte har markerat att "
                       u"de svarar för några bibliotek eller för att flera enkäter svarar för "
                       u"samma bibliotek. Alternativt saknar bibliotekten kommunkod eller huvudman.").format(
                message, len(survey_response_ids) - num_successful_published)
    else:
        surveys = Survey.objects.filter(id__in=survey_response_ids)
        for survey in surveys.filter(_status="published"):
            survey.status = status
            survey.save()

        surveys.filter(_status__ne="published").update(set___status=status)
        message = u"Ändrade status på {} stycken enkäter.".format(len(survey_response_ids))

    request.session["message"] = message
    return _surveys_redirect(request)


def _create_surveys(libraries, sample_year, ignore_missing_variables=False):
    template_cells = survey_template(sample_year).cells

    variables = {}  # Fetch variables once for IO-performance
    for variable in Variable.objects.all():
        variables[variable.key] = variable

    existing_surveys = {}
    for survey in Survey.objects.filter(sample_year=int(sample_year)):
        existing_surveys[survey.library.sigel] = survey

    created = 0
    for library in libraries:
        if library.sigel in existing_surveys:
            survey = existing_surveys[library.sigel]
            survey.library = library
        else:
            survey = Survey(
                library=library,
                sample_year=sample_year,
                observations=[])
            for cell in template_cells:
                variable_key = cell.variable_key
                if not variable_key in variables:
                    if ignore_missing_variables:
                        continue
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

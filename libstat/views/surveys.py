# -*- coding: utf-8 -*-
import logging
import json
from time import strftime
from datetime import datetime

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseServerError, HttpResponseBadRequest, HttpResponseForbidden
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.views.decorators.csrf import csrf_exempt
from openpyxl.writer.excel import save_virtual_workbook

from bibstat import settings
from libstat import utils
from libstat.services.bibdb_integration import fetch_libraries
from libstat.services.clean_data import remove_empty_surveys, match_libraries_and_replace_sigel
from libstat.models import Survey, SurveyObservation, Variable
from libstat.services.excel_export import surveys_to_excel_workbook, public_excel_workbook
from libstat.survey_templates import survey_template
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
    exclude_co_reported_by_other = request.GET.get("exclude_co_reported_by_other", False)

    email_choices = [("all", "Oavsett email"), ("with", "Med email"), ("invalid", "Med ogiltig email"),
                     ("without", "Utan email")]
    email = request.GET.get("email", "all")

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
            with_email=(email == "with"),
            without_email=(email == "without"),
            invalid_email=(email == "invalid"),
            is_active=True,
            exclude_co_reported_by_other=exclude_co_reported_by_other)
        inactive_surveys = Survey.objects.by(
            sample_year=sample_year,
            target_group=target_group,
            status=status,
            municipality_code=municipality_code,
            free_text=free_text,
            with_email=(email == "with"),
            without_email=(email == "without"),
            invalid_email=(email == "invalid"),
            is_active=False,
            exclude_co_reported_by_other=exclude_co_reported_by_other)
        surveys = active_surveys if surveys_state == "active" else inactive_surveys

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
        'email': email,
        'email_choices': email_choices,
        'surveys_state': surveys_state,
        'exclude_co_reported_by_other': exclude_co_reported_by_other,
        'survey_responses': surveys,
        'message': message,
        'survey_base_url': reverse("surveys"),
        'url_base': settings.API_BASE_URL,
        'bibdb_library_base_url': u"{}/library".format(settings.BIBDB_BASE_URL),
        'nav_surveys_css': 'active',
        'num_active_surveys': len(active_surveys),
        'num_inactive_surveys': len(inactive_surveys)
    }

    return render(request, 'libstat/surveys.html', context)


@permission_required('is_superuser', login_url='index')
def surveys_activate(request):
    if request.method == "POST":
        survey_ids = request.POST.getlist("survey-response-ids", [])
        Survey.objects.filter(pk__in=survey_ids).update(set__is_active=True)
        request.session["message"] = "Aktiverade {} stycken enkäter.".format(len(survey_ids))
        return _surveys_redirect(request)


@permission_required('is_superuser', login_url='index')
def surveys_inactivate(request):
    if request.method == "POST":
        survey_ids = request.POST.getlist("survey-response-ids", [])
        Survey.objects.filter(pk__in=survey_ids).update(set__is_active=False)
        request.session["message"] = "Inaktiverade {} stycken enkäter.".format(len(survey_ids))
        return _surveys_redirect(request)


def _surveys_redirect(request):
    if request.method == "GET":
        method = request.GET
    elif request.method == "POST":
        method = request.POST

    sample_year = method.get("sample_year", "")
    municipality_code = method.get("municipality_code", "")
    target_group = method.get("target_group", "")
    status = method.get("status", "")
    email = method.get("email", "")
    free_text = method.get("free_text", "")
    surveys_state = method.get("surveys_state", "")

    return HttpResponseRedirect(u"{}{}".format(
        reverse("surveys"),
        u"?action=list&sample_year={}&municipality_code={}&target_group={}&status={}&email={}&free_text={}&surveys_state={}".
        format(sample_year, municipality_code, target_group, status, email, free_text, surveys_state)))


@permission_required('is_superuser', login_url='index')
def surveys_export(request):
    if request.method == "POST":
        survey_ids = request.POST.getlist("survey-response-ids", [])
        filename = u"Exporterade enkätsvar ({}).xlsx".format(strftime("%Y-%m-%d %H.%M.%S"))
        workbook = surveys_to_excel_workbook(survey_ids)

        response = HttpResponse(save_virtual_workbook(workbook), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = u'attachment; filename="{}"'.format(filename)
        return response


@permission_required('is_superuser', login_url='index')
def surveys_overview(request, sample_year):
    table = [[""]]
    for status in Survey.STATUSES:
        table[0].append(status[1])
    table[0].append("Total")

    all_active_surveys = list(Survey.objects.filter(is_active=True, sample_year=sample_year)) #Preload surveys from database

    for library_type in utils.SURVEY_TARGET_GROUPS:
        row = [library_type[1]]
        library_type_value = library_type[0]
        for status in Survey.STATUSES:
            status_value = status[0]
            surveys = [s for s in all_active_surveys if s._status == status_value and s.library.library_type == library_type_value]
            surveys_all_count = len(surveys)
            surveys_self_reporting_count = len([s for s in surveys if s.library.sigel in s.selected_libraries])
            row.append('%d (%d)' % (surveys_self_reporting_count, surveys_all_count))

        surveys_total_status = [s for s in all_active_surveys if s.library.library_type == library_type_value]
        surveys_total_status_all_count = len(surveys_total_status)
        surveys_total_status_self_reporting_count = len([s for s in surveys_total_status if s.library.sigel in s.selected_libraries])
        row.append('%d (%d)' % (surveys_total_status_self_reporting_count, surveys_total_status_all_count))

        table.append(row)

    row = ["Total"]
    for status in Survey.STATUSES:
        status_value_str = status[0]
        surveys_total = [s for s in all_active_surveys if s._status == status_value_str]
        surveys_total_all_count = len(surveys_total)
        surveys_total_self_reporting_count = len([s for s in surveys_total if s.library.sigel in s.selected_libraries])
        row.append('%d (%d)' % (surveys_total_self_reporting_count, surveys_total_all_count))

    surveys_total_total_all_count = len(all_active_surveys)
    surveys_total_total_self_reporting_count = len([s for s in all_active_surveys if s.library.sigel in s.selected_libraries])
    row.append('%d (%d)' % (surveys_total_total_self_reporting_count, surveys_total_total_all_count))

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
                       u"samma bibliotek. Alternativt saknar biblioteken kommunkod eller huvudman.").format(
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

    created = 0
    for library in libraries:
        existing_surveys = Survey.objects.filter(sample_year=sample_year, library__sigel=library.sigel).only("library")
        if existing_surveys.count() != 0:
            survey = existing_surveys[0]
            survey.library = library
        else:
            survey = Survey(
                library=library,
                sample_year=sample_year,
                observations=[])
            for cell in template_cells:
                variable_key = cell.variable_key
                if variable_key not in variables:
                    if ignore_missing_variables:
                        continue
                    raise Exception("Can't find variable with key '{}'".format(variable_key))
                survey.observations.append(SurveyObservation(variable=variables[variable_key]))
            created += 1

        survey.save()

    return created


def _create_new_collection(year):
    libraries = fetch_libraries()
    _create_surveys(libraries, year)


@permission_required('is_superuser', login_url='index')
def import_and_create(request):
    sample_year = request.POST.get("sample_year")
    sample_year = int(sample_year)
    _create_new_collection(sample_year)
    return redirect(reverse('surveys'))


@permission_required('is_superuser', login_url='index')
def remove_empty(request):
    sample_year = request.POST.get("sample_year")
    remove_mode = request.POST.get("remove_mode")
    sample_year = int(sample_year)
    remove_empty_surveys(sample_year, remove_mode)
    return redirect(reverse('surveys'))


@permission_required('is_superuser', login_url='index')
def match_libraries(request):
    sample_year = request.POST.get("sample_year")
    sample_year = int(sample_year)
    match_libraries_and_replace_sigel(sample_year)
    return redirect(reverse('surveys'))


def _update_library_from_json(survey, json_data):
    sigel = json_data.get("sigel", None)
    if sigel and sigel != "":
        survey.library.sigel = sigel
    name = json_data.get("name", None)
    if name and name != "":
        survey.library.name = name.strip()
    municipality_code = json_data.get("municipality_code", None)
    if municipality_code and municipality_code != "":
        survey.library.municipality_code = municipality_code
    library_type = json_data.get("library_type", None)
    if library_type and library_type != "":
        survey.library.library_type = library_type
    if json_data.get("address", None):
        location = next((a for a in json_data["address"] if a["address_type"] == "stat"), None)
        address = location["street"] if location and location["street"] else None
        if address and address != "":
            survey.library.address = address
        city = location["city"] if location and location["city"] else None
        if city and city != "":
            survey.library.city = city
        zip_code = location["zip_code"] if location and location["zip_code"] else None
        if zip_code and zip_code != "":
            survey.library.zip_code = zip_code
    contact = json_data.get("contact", None)
    if contact:
        email = contact.get("email", None)
        contact_type = contact.get("contact_type", None)
        if email and email != "" and contact_type and contact_type == "statans":
            survey.library.email = email
    return survey


@csrf_exempt
def surveys_update_library(request):

    if request.method == "POST":
        post_data = json.loads(request.body)
        if post_data:
            passw = getattr(settings, 'BIBDB_UPDATE_PASS')
            hasher = PBKDF2PasswordHasher()
            try:
                if not hasher.verify(passw, post_data['pass']):
                    logger.warn("Bibdb library data change sync: password check failed")
                    return HttpResponseForbidden('Password required')
            except:
                logger.warn("Bibdb library data change sync: password check failed")
                return HttpResponseForbidden('Password required')

            sigel = post_data.get("sigel", None)
            if sigel:
                existing_surveys = Survey.objects.filter(is_active=True, library__sigel=sigel).only("library")
                if existing_surveys.count() != 0:
                    for survey in existing_surveys:
                        survey = _update_library_from_json(survey, post_data)
                        survey.save()
                    logger.info("Bibdb library data change sync: updated survey data for sigel %s" % sigel)
                    return HttpResponse("Updated survey data for sigel %s" % sigel)
                else:
                    logger.info("Bibdb library data change sync: Tried to update survey data for sigel %s, but couldn't find any active surveys." % sigel)
                    return HttpResponse("Tried to update survey data for sigel %s, but couldn't find any active surveys." % sigel)
            else:
                logger.error("Bibdb library data change sync: library not found")
                return HttpResponseNotFound("Library not found")
        else:
            logger.error("Bibdb library data change sync: bad request")
            return HttpResponseBadRequest()
    logger.warn("Received illegal request to /surveys/update_library. HTTP-method: %s" % request.method)
    return HttpResponseNotAllowed(['POST'])



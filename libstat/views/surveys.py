# -*- coding: utf-8 -*-
import logging
from time import strftime

from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from bibstat import settings
from libstat import utils
from libstat.models import Survey, Dispatch, Library
from libstat.survey_templates import has_template, survey_template

logger = logging.getLogger(__name__)


@permission_required('is_superuser', login_url='index')
def surveys(request):
    surveys = []
    sample_years = Survey.objects.distinct("sample_year")
    sample_years.sort()
    sample_years.reverse()

    municipality_codes = Library.objects.distinct("municipality_code")
    municipality_codes.sort()

    target_group = request.GET.get("target_group", "")
    sample_year = request.GET.get("sample_year", str(sample_years[0]) if sample_years else "")
    municipality_code = request.GET.get("municipality_code", "")
    status = request.GET.get("status", "")
    message = request.session.pop("message", "")

    if not sample_year:
        message = u"Du måste ange för vilket år du vill lista enkätsvar."
    else:
        surveys = Survey.filter_by(
            sample_year=sample_year,
            target_group=target_group,
            status=status,
            municipality_code=municipality_code)

    context = {
        'sample_years': sample_years,
        'sample_year': sample_year,
        'municipality_codes': municipality_codes,
        'municipality_code': municipality_code,
        'survey_responses': surveys,
        'target_groups': utils.SURVEY_TARGET_GROUPS,
        'target_group': target_group,
        'status': status,
        'bibdb_library_base_url': u"{}/library".format(settings.BIBDB_BASE_URL),
        'message': message,
        'url_base': settings.API_BASE_URL
    }
    return render(request, 'libstat/surveys.html', context)


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


@permission_required('is_superuser', login_url='index')
def surveys_publish(request):
    MAX_PUBLISH_LIMIT = 500

    if request.method == "POST":
        survey_response_ids = request.POST.getlist("survey-response-ids", [])

        logger.info(u"Publish requested for {} survey response ids".format(len(survey_response_ids)))

        if len(survey_response_ids) > MAX_PUBLISH_LIMIT:
            survey_response_ids = survey_response_ids[:MAX_PUBLISH_LIMIT]
            logger.warning(
                u"That seems like an awful lot of objects to handle in one transaction, limiting to first {}".format(
                    MAX_PUBLISH_LIMIT))

        if len(survey_response_ids) > 0:
            s_responses = Survey.objects.filter(id__in=survey_response_ids)
            for sr in s_responses:
                try:
                    sr.publish()
                except Exception:
                    logger.error(u"Error when publishing survey response {}:".format(sr.id))

    return _surveys_redirect(request)


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

    surveys = Survey.objects.filter(id__in=survey_ids).order_by('_library__name')

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
def surveys_remove(request):
    if request.method == "POST":
        survey_response_ids = request.POST.getlist("survey-response-ids", [])
        surveys = Survey.objects.filter(id__in=survey_response_ids)
        for survey in surveys:
            Dispatch.objects.filter(survey=survey).delete()
            survey.delete()
        request.session["message"] = u"Tog bort {} enkäter.".format(len(surveys))
    return _surveys_redirect(request)


@permission_required('is_superuser', login_url='index')
def surveys_overview(request, sample_year):
    surveys = Survey.objects.filter(sample_year=sample_year)
    context = {
        "sample_year": sample_year,
        "statuses": Survey.STATUSES,
        "target_groups": utils.SURVEY_TARGET_GROUPS,
        "surveys": surveys
    }

    return render(request, "libstat/surveys_overview.html", context)


@permission_required('is_superuser', login_url='index')
def surveys_statuses(request):
    status = request.POST.get("new_status", "")
    survey_response_ids = request.POST.getlist("survey-response-ids", [])
    published_surveys = []
    for survey in Survey.objects.filter(id__in=survey_response_ids):
        if survey.is_published:
            published_surveys.append(survey)
        else:
            survey.status = status
            survey.save()
    message = u"Ändrade status på {} enkäter.".format(len(survey_response_ids) - len(published_surveys))
    if published_surveys:
        message = u"{} OBS! Kunde inte ändra status på {} enkäter eftersom de redan är publicerade.".format(
            message, len(published_surveys))

    request.session["message"] = message
    return _surveys_redirect(request)

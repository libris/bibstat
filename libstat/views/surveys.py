# -*- coding: utf-8 -*-
import logging
from time import strftime

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.decorators import permission_required
from excel_response import ExcelResponse

from bibstat import settings
from libstat import utils
from libstat.models import Survey, Dispatch
from libstat.forms import SurveyForm


logger = logging.getLogger(__name__)


@permission_required('is_superuser', login_url='index')
def surveys(request):
    surveys = []
    sample_years = Survey.objects.distinct("sample_year")
    sample_years.sort()
    sample_years.reverse()

    target_group = request.GET.get("target_group", "")
    sample_year = request.GET.get("sample_year", str(sample_years[0]) if sample_years else "")
    status = request.GET.get("status", "")
    message = request.session.pop("message", "")

    if not sample_year:
        message = u"Du måste ange för vilket år du vill lista enkätsvar."
    else:
        surveys = Survey.filter_by(
            sample_year=sample_year,
            target_group=target_group,
            status=status)

    context = {
        'sample_years': sample_years,
        'survey_responses': surveys,
        'target_group': target_group,
        'status': status,
        'sample_year': sample_year,
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
                    sr.publish(user=request.user)
                except Exception as e:
                    logger.error(u"Error when publishing survey response {}:".format(sr.id))
                    print e

    return _surveys_redirect(request)


@permission_required('is_superuser', login_url='index')
def surveys_export(request):
    if request.method == "POST":
        survey_response_ids = request.POST.getlist("survey-response-ids", [])
        responses = Survey.objects.filter(id__in=survey_response_ids).order_by('library_name')
        filename = u"Exporterade enkätsvar ({})".format(strftime("%Y-%m-%d %H.%M.%S"))

        rows = [[unicode(observation._source_key) for observation in responses[0].observations]]
        for response in responses:
            rows.append(
                [observation.value if observation.value else "" for observation in response.observations])

        return ExcelResponse(rows, filename)


def _save_survey_response_from_form(response, form):
    if form.is_valid():
        disabled_inputs = form.cleaned_data["disabled_inputs"].split(" ")
        unknown_inputs = form.cleaned_data["unknown_inputs"].split(" ")
        for field in form.cleaned_data:
            observation = response.get_observation(field)
            if field in ("disabled_inputs", "id_key"):
                pass
            elif field == "submit_action":
                action = form.cleaned_data[field]
                if action == "submit" and response.status == "initiated":
                    response.status = "submitted"
            elif observation:
                observation.value = form.cleaned_data[field]
                observation.disabled = (field in disabled_inputs)
                observation.value_unknown = (field in unknown_inputs)
            else:
                response.__dict__["_data"][field] = form.cleaned_data[field]
        response.save()
    else:
        raise Exception(form.errors)


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
        "statuses": utils.SURVEY_RESPONSE_STATUSES,
        "target_groups": utils.SURVEY_TARGET_GROUPS,
        "surveys": surveys
    }

    return render(request, "libstat/surveys_overview.html", context)


def survey(request, survey_id):

    def has_password():
        return request.method == "GET" and "p" in request.GET or request.method == "POST"

    def get_password():
        return request.GET["p"] if request.method == "GET" else request.POST.get("password", None)

    def can_view_survey(survey):
        return request.user.is_authenticated() or request.session.get("password") == survey.id

    try:
        survey = Survey.objects.get(pk=survey_id)
    except Survey.DoesNotExist:
        return HttpResponseNotFound()

    context = {
        'survey_id': survey_id,
    }

    if not request.user.is_superuser:
        context["hide_navbar"] = True

    if can_view_survey(survey):
        if request.method == "POST":
            form = SurveyForm(request.POST, instance=survey)
            _save_survey_response_from_form(survey, form)

        if not request.user.is_authenticated() and survey.status == "not_viewed":
            survey.status = "initiated"
            survey.save()

        context["form"] = SurveyForm(instance=survey, authenticated=request.user.is_authenticated())
        return render(request, 'libstat/survey.html', context)

    if has_password():
        if get_password() == survey.password:
            request.session["password"] = survey.id
            request.session.set_expiry(0)
            return redirect(reverse("survey", args=(survey_id,)))
        else:
            context["wrong_password"] = True

    return render(request, 'libstat/survey/password.html', context)


@permission_required('is_superuser', login_url='index')
def surveys_status(request, survey_id):
    if request.method == "POST":
        status = request.POST[u'selected_status']
        survey = Survey.objects.get(pk=survey_id)
        survey.status = status
        survey.save()

    return redirect(reverse('survey', args=(survey_id,)))


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

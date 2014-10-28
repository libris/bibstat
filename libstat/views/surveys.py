# -*- coding: utf-8 -*-
import logging
from time import strftime

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.decorators import permission_required
from excel_response import ExcelResponse

from bibstat import settings
from libstat.models import Survey, Variable, SurveyObservation, Library, Dispatch
from libstat.forms import SurveyForm
from libstat.utils import survey_response_statuses


logger = logging.getLogger(__name__)


@permission_required('is_superuser', login_url='index')
def surveys(request):
    s_responses = []

    sample_years = Survey.objects.distinct("sample_year")
    sample_years.sort()
    sample_years.reverse()

    action = request.GET.get("action", "")
    target_group = request.GET.get("target_group", "")
    sample_year = request.GET.get("sample_year", "")
    status = request.GET.get("status", "")
    message = request.session.pop("message", "")

    if action == "list":
        if sample_year or target_group or status:
            s_responses = Survey.objects.by(
                sample_year=sample_year,
                target_group=target_group,
                status=status).order_by("library")
        else:
            message = u"Ange åtminstone ett urvalskriterium för att lista enkätsvar"

    context = {
        'sample_years': sample_years,
        'survey_responses': s_responses,
        'target_group': target_group,
        'status': status,
        'sample_year': sample_year,
        'bibdb_library_base_url': u"{}/library".format(settings.BIBDB_BASE_URL),
        'message': message,
        'url_base': settings.API_BASE_URL
    }
    return render(request, 'libstat/surveys.html', context)


@permission_required('is_superuser', login_url='index')
def surveys_publish(request):
    MAX_PUBLISH_LIMIT = 500

    if request.method == "POST":
        target_group = request.POST.get("target_group", "")
        sample_year = request.POST.get("sample_year", "")
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

    # TODO: There has to be a better way to do this...
    return HttpResponseRedirect(u"{}{}".format(
        reverse("surveys"),
        u"?action=list&target_group={}&sample_year={}".format(target_group, sample_year)))


def _render_dispatch(text, survey):

    text = text.replace("{bibliotek}", survey.library.name)
    text = text.replace("{enkätadress}", "")
    text = text.replace("{lösenord}", "")

    return text


@permission_required('is_superuser', login_url='index')
def surveys_dispatch(request):
    if request.method == "POST":
        survey_ids = request.POST.getlist("survey-response-ids", [])
        surveys = Survey.objects.filter(id__in=survey_ids)

        for survey in surveys:
            Dispatch(
                message=request.POST["message"],
                title=request.POST["title"],
                description=request.POST["description"],
                survey=survey
            ).save()

    return redirect(reverse("dispatches"))


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


def _survey_response_from_template(template, create_non_existing_variables=False):
    library = Library.objects.get(name=u"Motala stadsbibliotek")
    response = Survey(
        library_name=library.name,
        library=library,
        sample_year=2014,
        target_group="public",
        observations=[]
    )
    for section in template.sections:
        for group in section.groups:
            for row in group.rows:
                for cell in row.cells:
                    try:
                        v = Variable.objects.get(key=cell.variable_key)
                    except Exception:
                        if create_non_existing_variables:
                            v = Variable(
                                key=cell.variable_key,
                                description=u"",
                                is_public=False,
                                type=u"integer",
                                target_groups=["public", "research", "hospital", "school"]
                            )
                            v.save_updated_self_and_modified_replaced([])
                        else:
                            raise Exception(
                                "Can't create SurveyResponse with non-existing Variable " + cell.variable_key)
                    response.observations.append(SurveyObservation(variable=v))

    print(response)
    return response


def _save_survey_response_from_form(response, form):
    if form.is_valid():
        disabled_inputs = form.cleaned_data["disabled_inputs"].split(" ")
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
            else:
                response.__dict__["_data"][field] = form.cleaned_data[field]
        response.save()
    else:
        raise Exception(form.errors)


@permission_required('is_superuser', login_url='index')
def surveys_remove(request):
    if request.method == "POST":
        survey_response_ids = request.POST.getlist("survey-response-ids", [])
        Survey.objects.filter(id__in=survey_response_ids).delete()
        request.session["message"] = u"En eller flera enkäter har tagits bort"
    return redirect("surveys")


def survey(request, survey_id, wrong_password=False):
    try:
        survey = Survey.objects.get(pk=survey_id)
    except Survey.DoesNotExist:
        return HttpResponseNotFound()

    if request.user.is_authenticated() or request.session.get("password"):
        if request.method == "POST":
            form = SurveyForm(request.POST, instance=survey)
            _save_survey_response_from_form(survey, form)

        if not request.user.is_authenticated() and survey.status == "not_viewed":
            survey.status = "initiated"
            survey.save()

        context = {"form": SurveyForm(instance=survey, authenticated=request.user.is_authenticated())}
        return render(request, 'libstat/edit_survey.html', context)

    if request.method == "POST":
        password = request.POST["password"]
        if password == survey.password:
            request.session["password"] = True
            return redirect(reverse("survey", args=(survey_id,)))
        else:
            wrong_password = True

    return render(request, 'libstat/survey_password.html', {'survey_id': survey_id, 'wrong_password': wrong_password})


def _get_status_key_from_value(status):
    keys = list(survey_response_statuses.keys())
    values = list(survey_response_statuses.values())
    return keys[values.index(status)]


@permission_required('is_superuser', login_url='index')
def surveys_status(request, survey_id):
    if request.method == "POST":
        status = request.POST[u'selected_status']
        if status == "published":
            raise Exception("Cannot set published status for survey '" + survey_id + "'.")
        if not status in survey_response_statuses.values():
            raise Exception("Invalid status '" + status + "' for survey '" + survey_id + "'.")

        survey = Survey.objects.get(pk=survey_id)
        survey.status = _get_status_key_from_value(status)
        survey.save()

    return redirect(reverse('survey', args=(survey_id,)))

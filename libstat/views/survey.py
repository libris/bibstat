import logging
import time
import json
from datetime import datetime, timedelta, date

from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import permission_required
from django.forms.utils import ErrorList

from bibstat import settings

from libstat.models import Survey, Variable, SurveyObservation, Library, SurveyEditingLock
from libstat.forms.survey import SurveyForm
from libstat.survey_templates import survey_template

logger = logging.getLogger(__name__)


def example_survey(request):
    sample_year = date.today().year - 1

    context = {
        "hide_navbar": True,
        "hide_bottom_bar": True,
        "hide_admin_panel": True,
        "form": SurveyForm(survey=Survey(
            sample_year=sample_year,
            library=Library(
                name=u"Exempelbiblioteket",
                sigel=u"exempel_sigel",
                email=u"exempel@email.com",
                city=u"Exempelstaden",
                municipality_code=180,
                address=u"Exempelgatan 14B",
                library_type=u"folkbib"
            ),
            observations=[SurveyObservation(variable=Variable.objects.get(key=cell.variable_key))
                          for cell in survey_template(sample_year).cells])),
    }
    return render(request, 'libstat/survey.html', context)


@permission_required('is_superuser', login_url='index')
def sigel_survey(request, sigel):
    if request.method == 'GET':
        survey = Survey.objects.filter(library__sigel=sigel).first()
        if survey:
            logger.info('Redirecting to /survey/%s' % survey.id)
            return redirect(reverse('survey', args=(survey.id,)))
        return HttpResponseNotFound()


def _save_survey_response_from_form(survey, form):

    # Note: all syntax/format validation is done on client side w Bootstrap validator. 
    # All fields are handled as CharFields in the form and casted based on variable.type before saving.  More types can be added when needed.

    if form.is_valid():
        disabled_inputs = form.cleaned_data.pop("disabled_inputs").split(" ")
        unknown_inputs = form.cleaned_data.pop("unknown_inputs").split(" ")
        submit_action = form.cleaned_data.pop("submit_action", None)
        altered_fields = form.cleaned_data.pop("altered_fields", None).split(" ")

        variables = Variable.objects.all().only('key')
        all_variable_keys = [var.key for var in variables]

        for field in form.cleaned_data:
            value = form.cleaned_data[field]
            if type(value) == "str":
                value = value.strip()
            if field in all_variable_keys:
                variable_type = Variable.objects.filter(key=field).first().type
                if variable_type == "integer" and value != "" and value != "-":
                    # spaces are used as thousands separators
                    value = int(value.replace(" ", ""))
                elif variable_type == "decimal" and value != "" \
                        and value != "-":
                    # decimals are entered with comma in the form
                    # spaces are used as thousands separators
                    value = float(value.replace(" ", "").replace(",", "."))
            observation = survey.get_observation(field)
            if observation:
                if field in altered_fields:
                    observation.value = value
                    observation.disabled = (field in disabled_inputs)
                    observation.value_unknown = (field in unknown_inputs)
            else:
                survey.__dict__["_data"][field] = value

        survey.selected_libraries = filter(None, form.cleaned_data["selected_libraries"].split(" "))

        if submit_action == "submit" and survey.status in ("not_viewed", "initiated"):
            if not survey.has_conflicts():
                survey.status = "submitted"

        survey.save()

    else:
        logger.error('Could not save survey due to django validation error, library: %s' % survey.library.sigel)
        logger.error(form.errors)
        raise Exception(form.errors)


def survey(request, survey_id):
    def has_password():
        return request.method == "GET" and "p" in request.GET or request.method == "POST"

    def get_password():
        return request.GET["p"] if request.method == "GET" else request.POST.get("password", None)

    def can_view_survey(survey):
        return request.user.is_authenticated or request.session.get("password") == survey.id

    survey = Survey.objects.filter(pk=survey_id)
    if len(survey) != 1:
        return HttpResponseNotFound()

    survey = survey[0]

    if not survey.is_active and not request.user.is_authenticated:
        return HttpResponseForbidden()

    context = {
        'survey_id': survey_id,
    }

    if not request.user.is_superuser:
        context["hide_navbar"] = True

    if not request.user.is_authenticated and settings.BLOCK_SURVEY:
        return render(request, "libstat/survey_blocked.html")

    if can_view_survey(survey):

        if not request.user.is_authenticated and survey.status == "not_viewed":
            survey.status = "initiated"
            survey.save()

        if request.method == "POST":
            form = SurveyForm(request.POST, survey=survey)
            errors = _save_survey_response_from_form(survey, form) # Errors returned as separate json
            logger.debug("ERRORS: ")
            logger.debug(json.dumps(errors))
            return HttpResponse(json.dumps(errors), content_type="application/json")

        else:

            # if not request.user.is_superuser:
            #
            #     # Check survey lock before returning survey form
            #     # Each survey is locked to one session for a maximum of SURVEY_EDITING_LOCK_TIMEOUT_HOURS, or until browser window unloads
            #     survey_lock = SurveyEditingLock.objects.filter(survey_id=survey.id).first()
            #     if survey_lock:
            #         if datetime.utcnow() < survey_lock.date_locked + timedelta(hours=settings.SURVEY_EDITING_LOCK_TIMEOUT_HOURS):
            #             return render(request, 'libstat/locked.html')
            #         else: # There is a lock but it has timed out
            #             survey_lock.renew_lock()
            #     else: # Lock
            #         SurveyEditingLock.lock_survey(survey.id)

            context["form"] = SurveyForm(survey=survey, authenticated=request.user.is_authenticated)
            return render(request, 'libstat/survey.html', context)

    if has_password():
        if get_password() == survey.password:
            request.session["password"] = survey.id
            return redirect(reverse("survey", args=(survey_id,)))
        else:
            context["wrong_password"] = True

    return render(request, 'libstat/survey/password.html', context)


def release_survey_lock(request, survey_id):
    if request.method == "GET":
        if SurveyEditingLock.release_lock_on_survey(survey_id):
            return HttpResponse()
        else:
            return HttpResponseNotFound()
    return HttpResponseNotAllowed(permitted_methods=['GET'])


@permission_required('is_superuser', login_url='index')
def survey_status(request, survey_id):
    if request.method == "POST":
        survey = Survey.objects.get(pk=survey_id)
        survey.status = request.POST[u'selected_status']
        survey.save()

    return redirect(reverse('survey', args=(survey_id,)))


@permission_required('is_superuser', login_url='index')
def survey_notes(request, survey_id):
    if request.method == "POST":
        survey = Survey.objects.get(pk=survey_id)
        survey.notes = request.POST[u'notes']
        survey.save()

    return redirect(reverse('survey', args=(survey_id,)))

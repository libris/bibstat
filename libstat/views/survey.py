import logging
import json
from datetime import date

from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import (
    HttpResponseNotFound,
    HttpResponseForbidden,
    HttpResponse,
    HttpResponseNotAllowed,
)
from django.contrib.auth.decorators import permission_required

from bibstat import settings

from libstat.models import (
    Survey,
    Variable,
    SurveyObservation,
    Library,
    SurveyEditingLock,
)
from libstat.forms.survey import SurveyForm
from libstat.survey_templates import survey_template
from libstat.utils import get_log_prefix

logger = logging.getLogger(__name__)


def example_survey(request):
    sample_year = date.today().year - 1

    context = {
        "hide_navbar": True,
        "hide_bottom_bar": True,
        "hide_admin_panel": True,
        "form": SurveyForm(
            survey=Survey(
                sample_year=sample_year,
                library=Library(
                    name="Exempelbiblioteket",
                    sigel="exempel_sigel",
                    email="exempel@email.com",
                    city="Exempelstaden",
                    municipality_code=180,
                    address="Exempelgatan 14B",
                    library_type="folkbib",
                ),
                observations=[
                    SurveyObservation(
                        variable=Variable.objects.get(key=cell.variable_key)
                    )
                    for cell in survey_template(sample_year).cells
                ],
            )
        ),
    }
    return render(request, "libstat/survey.html", context)


@permission_required("is_superuser", login_url="index")
def sigel_survey(request, sigel):
    if request.method == "GET":
        survey = Survey.objects.filter(library__sigel=sigel).first()
        if survey:
            logger.info("Redirecting to /survey/%s" % survey.id)
            return redirect(reverse("survey", args=(survey.id,)))
        return HttpResponseNotFound()


def _save_survey_response_from_form(survey, form, log_prefix):
    # Note: all syntax/format validation is done on client side w Bootstrap validator.
    # All fields are handled as CharFields in the form and casted based on variable.type before saving.
    # More types can be added when needed.

    if form.is_valid():
        disabled_inputs = form.cleaned_data.pop("disabled_inputs").split(" ")
        unknown_inputs = form.cleaned_data.pop("unknown_inputs").split(" ")
        submit_action = form.cleaned_data.pop("submit_action", None)
        altered_fields = form.cleaned_data.pop("altered_fields", None).split(" ")

        variables = Variable.objects.all().only("key")
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
                elif variable_type == "decimal" and value != "" and value != "-":
                    # decimals are entered with comma in the form
                    # spaces are used as thousands separators
                    value = float(value.replace(" ", "").replace(",", "."))
            observation = survey.get_observation(field)
            if observation:
                if field in altered_fields:
                    observation.value = value
                    observation.disabled = field in disabled_inputs
                    observation.value_unknown = field in unknown_inputs
            else:
                survey._data[field] = value

        survey.selected_libraries = [
            _f for _f in form.cleaned_data["selected_libraries"].split(" ") if _f
        ]

        logger.info(f"{log_prefix} Saving form; submit_action={submit_action}, survey_status={survey.status}")
        if submit_action == "submit" and survey.status in ("not_viewed", "initiated"):
            if not survey.has_conflicts():
                logger.info(f"{log_prefix} submit_action was 'submit' and survey.status {survey.status}; changing status to submitted")
                survey.status = "submitted"
            else:
                logger.info(f"{log_prefix} submit_action was 'submit' and survey.status {survey.status}; however status NOT changed to submitted due to conflicts")

        survey.save(validate=False)

    else:
        logger.error(
            "Could not save survey due to django validation error, library: %s"
            % survey.library.sigel
        )
        logger.error(form.errors)
        raise Exception(form.errors)


def survey(request, survey_id):
    def has_password():
        return (
            request.method == "GET" and "p" in request.GET or request.method == "POST"
        )

    def get_password():
        return (
            request.GET["p"]
            if request.method == "GET"
            else request.POST.get("password", None)
        )

    def can_view_survey(survey):
        return (
            request.user.is_authenticated
            or request.session.get("password") == survey.id
        )

    survey = Survey.objects.filter(pk=survey_id)
    if len(survey) != 1:
        return HttpResponseNotFound()

    survey = survey[0]
    log_prefix = get_log_prefix(request, survey_id, survey)

    if not survey.is_active and not request.user.is_authenticated:
        logger.info(f"{log_prefix} tried to {request.method} but survey is not active and user is not authenticated")
        return HttpResponseForbidden()

    context = {
        "survey_id": survey_id,
    }

    if not request.user.is_superuser:
        context["hide_navbar"] = True

    if not request.user.is_authenticated and settings.BLOCK_SURVEY:
        return render(request, "libstat/survey_blocked.html")

    if can_view_survey(survey):

        if not request.user.is_authenticated and survey.status == "not_viewed":
            logger.info(f"{log_prefix} User not authenticated and survey.status was not_viewed; setting survey.status to initiated and saving")
            survey.status = "initiated"
            survey.save(validate=False)

        if request.method == "POST":
            # Only superuser is allowed to edit surveys that have already been submitted
            if (
                survey.status not in ["not_viewed", "initiated"]
                and not request.user.is_superuser
            ):
                logger.error(
                    f"{log_prefix} Refusing to save because survey has status submitted (or higher), library {survey.library.sigel}"
                )
                return HttpResponse(
                    json.dumps({"error": "Survey already submitted"}),
                    status=409,
                    content_type="application/json",
                )
            else:
                logger.info(f"{log_prefix} POSTing survey")
                form = SurveyForm(request.POST, survey=survey)
                errors = _save_survey_response_from_form(
                    survey, form, log_prefix
                )  # Errors returned as separate json
                if errors:
                    logger.info(f"{log_prefix} Errors when saving survey: {json.dumps(errors)}")
                else:
                    logger.info(f"{log_prefix} Survey saved")
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

            context["form"] = SurveyForm(
                survey=survey, authenticated=request.user.is_authenticated
            )
            return render(request, "libstat/survey.html", context)

    if has_password():
        if get_password() == survey.password:
            request.session["password"] = survey.id
            return redirect(reverse("survey", args=(survey_id,)))
        else:
            context["wrong_password"] = True

    # If user is trying to save the form but isn't authenticated, respond with a 401
    if (
        request.method == "POST"
        and not request.POST.get("password", None)
        and not can_view_survey(survey)
    ):
        logger.info(f"{log_prefix} Tried saving, but unauthorized")
        return HttpResponse("Unauthorized", status=401)

    # Otherwise, show the password page
    return render(request, "libstat/survey/password.html", context)


def release_survey_lock(request, survey_id):
    if request.method == "GET":
        if SurveyEditingLock.release_lock_on_survey(survey_id):
            return HttpResponse()
        else:
            return HttpResponseNotFound()
    return HttpResponseNotAllowed(permitted_methods=["GET"])


@permission_required("is_superuser", login_url="index")
def survey_status(request, survey_id):
    if request.method == "POST":
        survey = Survey.objects.get(pk=survey_id)
        log_prefix = f"{get_log_prefix(request, survey_id, survey)}"
        logger.info(f"{log_prefix} Changing selected_status from {survey.status} to {request.POST['selected_status']}")
        survey.status = request.POST["selected_status"]
        survey.save()

    return redirect(reverse("survey", args=(survey_id,)))


@permission_required("is_superuser", login_url="index")
def survey_notes(request, survey_id):
    if request.method == "POST":
        survey = Survey.objects.get(pk=survey_id)
        log_prefix = f"{get_log_prefix(request, survey_id, survey)}"
        logger.info(f"{log_prefix} Adding notes to survey")
        survey.notes = request.POST["notes"]
        survey.save()

    return redirect(reverse("survey", args=(survey_id,)))

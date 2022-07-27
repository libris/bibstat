import logging

from django.contrib.auth.decorators import permission_required
from django.core.mail import get_connection, EmailMultiAlternatives
from django.urls import reverse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from bibstat import settings
from libstat.models import Dispatch, Survey

logger = logging.getLogger(__name__)


def _rendered_template(template, survey):
    survey_url = settings.API_BASE_URL + reverse("survey", args=(survey.id,))
    survey_url_with_password = survey_url + "?p=" + survey.password

    rendered = template.replace(
        "{bibliotek}", survey.library.name if survey.library.name else ""
    )
    rendered = rendered.replace(
        "{ort}", survey.library.city if survey.library.city else ""
    )
    rendered = rendered.replace("{lösenord}", survey.password)
    rendered = rendered.replace("{enkätadress}", survey_url)
    rendered = rendered.replace(
        "{enkätadress (med lösenord)}", survey_url_with_password
    )

    return rendered


@permission_required("is_superuser", login_url="login")
def dispatches(request):
    if request.method == "POST":
        survey_ids = request.POST.getlist("survey-response-ids", [])
        surveys = list(Survey.objects.filter(id__in=survey_ids).exclude("observations"))

        dispatches = [
            Dispatch(
                message=_rendered_template(request.POST.get("message", None), survey),
                title=_rendered_template(request.POST.get("title", None), survey),
                description=request.POST.get("description", None),
                library_name=survey.library.name,
                library_email=survey.library.email,
                library_city=survey.library.city,
            )
            for survey in surveys
        ]

        Dispatch.objects.insert(dispatches, load_bulk=False)

        return redirect(reverse("dispatches"))

    if request.method == "GET":
        context = {
            "dispatches": list(Dispatch.objects.all()),
            "message": request.session.pop("message", None),
            "nav_dispatches_css": "active",
        }

        return render(request, "libstat/dispatches.html", context)


@permission_required("is_superuser", login_url="login")
def dispatches_delete(request):
    if request.method == "POST":
        dispatch_ids = request.POST.getlist("dispatch-ids", [])
        Dispatch.objects.filter(id__in=dispatch_ids).delete()

        message = ""
        if len(dispatch_ids) == 0:
            message = "Inga utskick togs bort från utkorgen."
        elif len(dispatch_ids) >= 1:
            message = "{} utskick togs bort från utkorgen.".format(len(dispatch_ids))

        request.session["message"] = message
        return redirect(reverse("dispatches"))


@permission_required("is_superuser", login_url="login")
def dispatches_send(request):
    if request.method == "POST":
        dispatch_ids = request.POST.getlist("dispatch-ids", [])
        dispatches = Dispatch.objects.filter(id__in=dispatch_ids)
        dispatches_with_email = [
            dispatch for dispatch in dispatches if dispatch.library_email
        ]

        def chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        sent_ids = []
        for dispatches_with_email_chunk in chunks(dispatches_with_email, 50):
            connection = get_connection()
            connection.open()
            for dispatch in dispatches_with_email_chunk:
                message = EmailMultiAlternatives(
                    dispatch.title,
                    dispatch.message,
                    settings.EMAIL_SENDER,
                    [dispatch.library_email],
                )
                html_content = render_to_string(
                    "libstat/email_template.html", {"message": dispatch.message}
                )
                message.attach_alternative(html_content, "text/html")
                try:
                    message.send()
                    sent_ids.append(dispatch.id)
                except:
                    pass
            connection.close()

        Dispatch.objects.filter(id__in=sent_ids).delete()

        def get_message(total, sent):
            message = ""
            if sent > 0:
                message = "Det har nu skickats iväg totalt {} {}.".format(
                    sent, "e-postmeddelande" if sent == 1 else "e-postmeddelanden"
                )

            failed = total - sent
            if failed > 0:
                if len(message) > 0:
                    message = message + "\n"
                message = (
                    message
                    + "Det fanns {} utskick utan e-postadress; {} har inte skickats.".format(
                        failed, "detta" if failed == 1 else "dessa"
                    )
                )

            return message

        request.session["message"] = get_message(len(dispatches), len(sent_ids))

    return redirect(reverse("dispatches"))

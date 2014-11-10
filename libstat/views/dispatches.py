# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import permission_required
from django.core.mail import send_mass_mail
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from bibstat import settings
from libstat.models import Dispatch, Survey


def _rendered_template(template, survey):
    survey_url = settings.API_BASE_URL + reverse('survey', args=(survey.id,))
    survey_url_with_password = survey_url + "?p=" + survey.password

    rendered = template.replace(u"{bibliotek}", survey.library.name)
    rendered = rendered.replace(u"{lösenord}", survey.password)
    rendered = rendered.replace(u"{enkätadress}", survey_url)
    rendered = rendered.replace(u"{enkätadress (med lösenord)}", survey_url_with_password)

    return rendered


@permission_required('is_superuser', login_url='login')
def dispatches(request):
    if request.method == "POST":
        survey_ids = request.POST.getlist("survey-response-ids", [])
        surveys = Survey.objects.filter(id__in=survey_ids)

        for survey in surveys:
            Dispatch(
                message=_rendered_template(request.POST.get("message", None), survey),
                title=_rendered_template(request.POST.get("title", None), survey),
                description=request.POST.get("description", None),
                survey=survey
            ).save()

        return redirect(reverse("dispatches"))

    if request.method == "GET":
        dispatches = [
            {
                "id": dispatch.id,
                "description": dispatch.description,
                "title": dispatch.title,
                "message": dispatch.message.replace("\n", "<br>"),
                "library_name": dispatch.survey.library.name,
                "library_city": dispatch.survey.library.city,
                "library_email": dispatch.survey.library.email,
            } for dispatch in Dispatch.objects.all()
        ]

        message = request.session.pop("message", None)
        return render(request, 'libstat/dispatches.html', {"dispatches": dispatches, "message": message})


@permission_required('is_superuser', login_url='login')
def dispatches_delete(request):
    if request.method == "POST":
        dispatch_ids = request.POST.getlist("dispatch-ids", [])
        Dispatch.objects.filter(id__in=dispatch_ids).delete()

        return redirect(reverse("dispatches"))


@permission_required('is_superuser', login_url='login')
def dispatches_send(request):
    if request.method == "POST":
        dispatch_ids = request.POST.getlist("dispatch-ids", [])
        dispatches = Dispatch.objects.filter(id__in=dispatch_ids)
        dispatches_with_email = [dispatch for dispatch in dispatches if dispatch.survey.library.email]

        messages = [
            (dispatch.title, dispatch.message, settings.EMAIL_SENDER, [dispatch.survey.library.email])
            for dispatch in dispatches_with_email
        ]

        send_mass_mail(messages)
        for dispatch in dispatches_with_email:
            dispatch.delete()

        def get_message(total, sent):
            message = ""
            if sent > 0:
                message = "Det har nu skickats iväg totalt {} {}.".\
                    format(sent, "e-postmeddelande" if sent == 1 else "e-postmeddelanden")

            failed = total - sent
            if failed > 0:
                if len(message) > 0:
                    message = message + "\n"
                message = message + "Det fanns {} utskick utan e-postadress; {} har inte skickats.".\
                    format(failed, "detta" if failed == 1 else "dessa")

            return message

        request.session["message"] = get_message(len(dispatches), len(dispatches_with_email))

    return redirect(reverse("dispatches"))
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
                message=_rendered_template(request.POST["message"], survey),
                title=_rendered_template(request.POST["title"], survey),
                description=request.POST["description"],
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

        return render(request, 'libstat/dispatches.html', {"dispatches": dispatches})


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

        messages = [
            (dispatch.title, dispatch.message, settings.EMAIL_SENDER, [dispatch.survey.library.email])
            for dispatch in dispatches
        ]

        send_mass_mail(messages)
        #dispatches.delete()

    return redirect(reverse("dispatches"))
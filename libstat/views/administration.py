# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required

from libstat.models import Survey
from libstat.views.surveys import _create_new_collection
from libstat.survey_templates import available_years


@permission_required('is_superuser', login_url='index')
def administration(request):
    context = {
        "possible_year_choices": available_years(),
        "message": request.session.pop("message", None),
        "nav_administration_css": "active"
    }

    return render(request, 'libstat/administration.html', context)


@permission_required('is_superuser', login_url='index')
def create_new_collection(request):
    year = request.POST.get("year")

    if int(year) in [int(year) for year in Survey.objects.distinct("sample_year")]:
        request.session["message"] = "Kan inte skapa en ny omgång för {}, den omgången finns redan".format(year)
        return redirect(reverse("administration"))
    elif year:
        _create_new_collection(year)
    return redirect(reverse('surveys'))

# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required

from libstat.models import Survey
from libstat.views.surveys import _create_new_collection


@permission_required('is_superuser', login_url='index')
def administration(request):
    context = {
        "possible_year_choices": [
            2014,
            2015,
            2016,
            2017,
            2018
        ],
        "message": request.session.pop("message", None)
    }

    return render(request, 'libstat/administration.html', context)


@permission_required('is_superuser', login_url='index')
def create_new_collection(request):
    sample_year = request.POST.get("year")

    if int(sample_year) in [int(year) for year in Survey.objects.distinct("sample_year")]:
        request.session["message"] = "Kan inte skapa en ny omgång för {}, den omgången finns redan.".format(sample_year)
        return redirect(reverse("administration"))
    elif sample_year:
        _create_new_collection(int(sample_year))
        return redirect(reverse('surveys'))

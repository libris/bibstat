# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required

from libstat.views.surveys import _create_new_collection
from libstat.survey_templates import available_years


@permission_required('is_superuser', login_url='index')
def administration(request):
    context = {
        "possible_year_choices": available_years()
    }

    return render(request, 'libstat/administration.html', context)


@permission_required('is_superuser', login_url='index')
def create_new_collection(request):
    year = request.POST.get("year")
    if year:
        _create_new_collection(year)
    return redirect(reverse('surveys'))

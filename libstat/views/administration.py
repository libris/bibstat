from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required

from libstat.models import Survey
from libstat.views.surveys import _create_new_collection

import datetime

current_year = datetime.datetime.now().year


@permission_required('is_superuser', login_url='index')
def administration(request):
    context = {
        "possible_year_choices": [
            current_year -1,
            current_year,
            current_year + 1,
            current_year + 2,
            current_year + 3,
            current_year + 4
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

# -*- coding: utf-8 -*-
from pprint import pprint
from django.core.urlresolvers import reverse

from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from data.municipalities import municipalities, get_counties
from data.principals import principal_for_library_type, name_for_principal, library_types_for_principal
from libstat.models import Survey
from libstat.services.report_generation import get_report


def report(request):
    if request.method == "GET":
        return redirect(reverse("reports"))

    previous_url = request.POST.get("previous_url", reverse("reports"))
    if not is_safe_url(url=previous_url, host=request.get_host()):
        return redirect(reverse("reports"))

    sample_year = int(request.POST.get("sample_year", None))
    sigels = request.POST.getlist("surveys", [])
    surveys = list(Survey.objects.filter(_status=u"published", sample_year=sample_year, library__sigel__in=sigels))

    context = get_report(surveys, sample_year)
    context["previous_url"] = previous_url

    return render(request, 'libstat/report.html', context)


def reports(request):
    def all_sample_years(surveys):
        _sample_years = surveys.distinct("sample_year")
        _sample_years.sort()
        _sample_years.reverse()
        return _sample_years

    def all_municipality_codes(surveys):
        _municipality_codes = surveys.distinct("library.municipality_code")
        _municipality_codes = [(municipalities[code], code) for code in _municipality_codes if code in municipalities]
        _municipality_codes += list(get_counties(_municipality_codes))
        _municipality_codes.sort()
        return _municipality_codes

    def all_principals(surveys):
        _principals = list(set(
            [principal_for_library_type[library_type] for library_type in surveys.distinct("library.library_type") if
             library_type in principal_for_library_type]))
        _principals = [(name_for_principal[p], p) for p in _principals]
        _principals.sort()
        return _principals

    if request.method == "GET":
        surveys = Survey.objects.filter(_status=u"published").exclude("observations").order_by("library.name")

        sample_year = request.GET.get("sample_year", "")
        municipality_code = request.GET.get("municipality_code", "")
        principal = request.GET.get("principal", "")

        sample_years = all_sample_years(surveys)
        municipality_codes = all_municipality_codes(surveys)
        principals = all_principals(surveys)

        message = None
        library_name_for_sigel = {}
        filtered_surveys = []

        if sample_year:
            filtered_surveys = surveys.filter(sample_year=sample_year)
            if municipality_code:
                if municipality_code.endswith(u"00"):  # County code
                    filtered_surveys = filtered_surveys.filter(
                        library__municipality_code__startswith=municipality_code[0:2])
                else:
                    filtered_surveys = filtered_surveys.filter(library__municipality_code=municipality_code)
            if principal:
                filtered_surveys = filtered_surveys.filter(
                    library__library_type__in=library_types_for_principal[principal])

            if len(surveys) == 0:
                message = u"Det finns inga bibliotek att visa för den valda verksamheten."
            else:
                sigels = [sigel for survey in filtered_surveys for sigel in survey.selected_libraries]
                for survey in Survey.objects.filter(library__sigel__in=sigels).only("library.sigel", "library.name"):
                    library_name_for_sigel[survey.library.sigel] = survey.library.name

        context = {
            "sample_year": sample_year,
            "sample_years": sample_years,
            "message": message,
            "surveys": filtered_surveys,
            "library_name_for_sigel": library_name_for_sigel,
            "municipality_code": municipality_code,
            "municipality_name": municipalities[municipality_code] if municipality_code in municipalities else None,
            "municipality_codes": municipality_codes,
            "principal": principal,
            "principals": principals
        }

        return render(request, 'libstat/reports.html', context)
# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from django.shortcuts import render, redirect
from data.municipalities import municipalities, get_counties
from data.principals import principal_for_library_type, name_for_principal, library_types_for_principal
from libstat.models import Survey
from libstat.reports import get_report


def report(request):
    if request.method == "GET":
        return redirect(reverse("reports"))

    sample_year = int(request.POST.get("sample_year", None))
    sigels = request.POST.getlist("surveys", [])

    surveys = list(Survey.objects.filter(sample_year=sample_year, library__sigel__in=sigels))

    context = get_report(surveys, sample_year)

    return render(request, 'libstat/report.html', context)


def reports(request):
    if request.method == "GET":
        surveys = Survey.objects.filter(_status=u"published")

        sample_year = request.GET.get("sample_year", "")
        sample_years = surveys.distinct("sample_year")
        sample_years.sort()

        municipality_code = request.GET.get("municipality_code", "")
        municipality_codes = surveys.distinct("library.municipality_code")
        municipality_codes = [(municipalities[code], code) for code in municipality_codes if code in municipalities]
        municipality_codes += list(get_counties(municipality_codes))
        municipality_codes.sort()

        def filter_municipality_code(surveys):
            if municipality_code.endswith(u"00"):  # County codes end with double zero
                return surveys.filter(library__municipality_code__startswith=municipality_code[0:2])
            else:
                return surveys.filter(library__municipality_code=municipality_code)

        principal = request.GET.get("principal", "")
        principals = list(set(
            [principal_for_library_type[library_type] for library_type in surveys.distinct("library.library_type") if
             library_type in principal_for_library_type]))
        principals = [(name_for_principal[p], p) for p in principals]
        principals.sort()

        def filter_with_parameters(surveys):
            surveys = surveys.filter(sample_year=sample_year)
            if municipality_code:
                surveys = filter_municipality_code(surveys)
            if principal:
                surveys = surveys.filter(library__library_type__in=library_types_for_principal[principal])

            return surveys

        message = None
        filtered_surveys = []
        library_name_for_sigel = None
        submit = request.GET.get("submit", False)

        if submit:
            if sample_year:
                filtered_surveys = list(filter_with_parameters(surveys).exclude("observations"))
                if len(filtered_surveys) > 0:
                    sigels = []
                    for survey in filtered_surveys:
                        for sigel in survey.selected_libraries:
                            sigels.append(sigel)

                    library_name_for_sigel = {}
                    surveys_with_sigels = Survey.objects.filter(library__sigel__in=sigels)
                    for survey in surveys_with_sigels.only("library.sigel", "library.name"):
                        library_name_for_sigel[survey.library.sigel] = survey.library.name
                else:
                    message = u"Det finns inga bibliotek att visa för valen av biblioteksverksamhet."

            else:
                message = u"Du måste välja ett verksamhetsår för att visa bibliotek."

        context = {
            "nav_reports_css": "active",
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
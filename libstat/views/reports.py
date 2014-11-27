# -*- coding: utf-8 -*-

from django.shortcuts import render
from data.municipalities import municipalities
from data.principals import principal_for_library_type, PRINCIPALS, name_for_principal
from libstat.models import Survey


def reports(request):
    if request.method == "GET":

        #surveys = Survey.objects.filter(_status=u"published") TODO Use this one instead.
        surveys = Survey.objects.all()

        sample_year = request.GET.get("sample_year", "")
        sample_years = surveys.distinct("sample_year")
        sample_years.sort()

        municipality_code = request.GET.get("municipality_code", "")
        municipality_codes = surveys.distinct("library.municipality_code")
        municipality_codes = [(municipalities[code], code) for code in municipality_codes if code in municipalities]
        municipality_codes.sort()

        principal = request.GET.get("principal", "")
        principals = list(set([principal_for_library_type[library_type] for library_type in surveys.distinct("library.library_type") if library_type in principal_for_library_type]))
        principals = [(name_for_principal[p], p) for p in principals]
        principals.sort()

        message = None
        submit = request.GET.get("submit", False)
        parameters = [sample_year, municipality_code, principal]
        if submit and not all(parameters):
            message = "Du måste göra ett val för "

            parameter_names = []
            if not sample_year: parameter_names.append("verksamhetsår")
            if not municipality_code: parameter_names.append("kommun/län")
            if not principal: parameter_names.append("huvudman")

            if len(parameter_names) > 2:
                message += "{} och {}.".format(", ".join(parameter_names[0:2]), parameter_names[2])
            else:
                message += " och ".join(parameter_names) + "."

        context = {
            "nav_reports_css": "active",
            "sample_year": sample_year,
            "sample_years": sample_years,
            "message": message,
            "municipality_code": municipality_code,
            "municipality_codes": municipality_codes,
            "principal": principal,
            "principals": principals
        }

        return render(request, 'libstat/reports.html', context)
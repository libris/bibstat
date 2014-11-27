# -*- coding: utf-8 -*-

from django.shortcuts import render
from data.municipalities import municipalities
from data.principals import principal_for_library_type, PRINCIPALS, name_for_principal, library_types_for_principal
from libstat.models import Survey


def reports(request):
    def missing_parameters_message(sample_year, municipality_code, principal):
        message = "Du måste göra ett val för "

        parameter_names = []
        if not sample_year: parameter_names.append("verksamhetsår")
        if not municipality_code: parameter_names.append("kommun/län")
        if not principal: parameter_names.append("huvudman")

        if len(parameter_names) > 2:
            message += "{} och {}.".format(", ".join(parameter_names[0:2]), parameter_names[2])
        else:
            message += " och ".join(parameter_names) + "."

        return message

    if request.method == "GET":
        surveys = Survey.objects.filter(_status=u"published")

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
        filtered_surveys = None
        library_name_for_sigel = None
        submit = request.GET.get("submit", False)

        parameters = [sample_year, municipality_code, principal]
        if submit:
            if all(parameters):
                filtered_surveys = list(surveys.filter(
                    sample_year=sample_year,
                    library__municipality_code=municipality_code,
                    library__library_type__in=library_types_for_principal[principal]
                ).exclude("observations"))

                sigels = []
                for survey in filtered_surveys:
                    for sigel in survey.selected_libraries:
                        sigels.append(sigel)

                library_name_for_sigel = {}
                for survey in Survey.objects.filter(
                        sample_year=sample_year,
                        library__municipality_code=municipality_code,
                        library__sigel__in=sigels
                ).only("library.sigel", "library.name"):
                    library_name_for_sigel[survey.library.sigel] = survey.library.name

            else:
                message = missing_parameters_message(sample_year, municipality_code, principal)

        context = {
            "nav_reports_css": "active",
            "sample_year": sample_year,
            "sample_years": sample_years,
            "message": message,
            "show_filtered_surveys": submit and all(parameters),
            "filtered_surveys": filtered_surveys,
            "library_name_for_sigel": library_name_for_sigel,
            "municipality_code": municipality_code,
            "municipality_codes": municipality_codes,
            "principal": principal,
            "principals": principals
        }

        return render(request, 'libstat/reports.html', context)
# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from django.shortcuts import render, redirect
from data.municipalities import municipalities
from data.principals import principal_for_library_type, name_for_principal, library_types_for_principal
from libstat.models import Survey
from libstat.survey_templates import survey_template


def report(request):
    if request.method == "GET":
        return redirect(reverse("administration"))

    sample_year = request.POST.get("sample_year", None)
    sigels = request.POST.getlist("surveys", [])

    surveys = []
    for survey in list(Survey.objects.filter(library__sigel__in=sigels)):
        surveys.append((survey, survey.previous_years_survey()))
    libraries = []
    for survey, _ in surveys:
        for sigel in survey.selected_libraries:
            library = Survey.objects.get(library__sigel=sigel).library
            libraries.append({
                "sigel": library.sigel,
                "name": library.name
            })

    cells = survey_template(sample_year).cells
    observations = []
    for cell in cells:
        if "integer" in cell.types or "decimal" in cell.types:
            value = 0
            previous_value = 0
            data_missing = False
            previous_data_missing = False
            for survey, previous_survey in surveys:
                observation = survey.get_observation(cell.variable_key)
                if observation and observation.value:
                    value += int(observation.value)
                else:
                    data_missing = True
                if observation and observation.variable:
                    prev_value = survey.previous_years_value(observation.variable,
                                                             previous_years_survey=previous_survey)
                    if prev_value:
                        previous_value += int(prev_value)
                    else:
                        previous_data_missing = True
                else:
                    previous_data_missing = True

            observations.append({
                "label": cell.variable.question_part,
                "value": value,
                "previous_value": previous_value,
                "difference": "-",
                "data_missing": data_missing,
                "previous_data_missing": previous_data_missing
            })

    context = {
        "sample_year": sample_year,
        "previous_year": int(sample_year) - 1,
        "libraries": libraries,
        "observations": observations
    }

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
        municipality_codes.sort()

        principal = request.GET.get("principal", "")
        principals = list(set(
            [principal_for_library_type[library_type] for library_type in surveys.distinct("library.library_type") if
             library_type in principal_for_library_type]))
        principals = [(name_for_principal[p], p) for p in principals]
        principals.sort()

        message = None
        filtered_surveys = []
        library_name_for_sigel = None
        submit = request.GET.get("submit", False)

        if submit:
            if sample_year:
                filtered_surveys = surveys.filter(sample_year=sample_year)
                if municipality_code:
                    filtered_surveys = filtered_surveys.filter(library__municipality_code=municipality_code)
                if principal:
                    filtered_surveys = filtered_surveys.filter(
                        library__library_type__in=library_types_for_principal[principal])

                filtered_surveys = list(filtered_surveys.exclude("observations"))
                if len(filtered_surveys) > 0:
                    sigels = []
                    for survey in filtered_surveys:
                        for sigel in survey.selected_libraries:
                            sigels.append(sigel)

                    library_name_for_sigel = {}
                    surveys_with_sigels = Survey.objects.filter(sample_year=sample_year)
                    if municipality_code:
                        surveys_with_sigels = surveys_with_sigels.filter(library__municipality_code=municipality_code)
                    if principal:
                        surveys_with_sigels = surveys_with_sigels.filter(
                            library__library_type__in=library_types_for_principal[principal])

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
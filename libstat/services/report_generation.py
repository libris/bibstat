# -*- coding: utf-8 -*-
from libstat.models import Survey, Variable, OpenData
from libstat.report_templates import report_template_2014, VariableRow, KeyFigureRow


def get_report(surveys, year):
    libraries = []
    for survey in surveys:
        for sigel in survey.selected_libraries:
            libraries.append(Survey.objects.get(sample_year=year, library__sigel=sigel).library)

    # This should of course be updated when (and if) more templates are added
    template = report_template_2014()

    observations = _get_observations_from(template, surveys, year)

    report = {
        "year": year,
        "libraries": libraries,
        "measurements": generate_report(template, year, observations)
    }

    return report


def generate_report(template, year, observations):
    def values_for(observations, variable_keys, year):
        return [float(observations.get(key, {}).get(year, 0)) for key in variable_keys]

    report = []
    for group in template.groups:
        report_group = {"title": group.title,
                        "years": [year - 1, year],
                        "rows": []}
        for row in group.rows:
            value = None
            previous_value = None
            total = None
            if isinstance(row, VariableRow):
                observation = observations.get(row.variable_key, {})
                value = observation.get(year, None)
                previous_value = observation.get(year - 1, None)
                total = observation.get("total", None)
            elif isinstance(row, KeyFigureRow):
                value = row.compute(values_for(observations, row.variable_keys, year))
                previous_value = row.compute(values_for(observations, row.variable_keys, year - 1))

            diff = ((value / previous_value) - 1) * 100 if value and previous_value else None
            nation_diff = (value / total) * 1000 if value and total else None

            report_row = {"label": row.description}
            if previous_value is not None: report_row[year - 1] = previous_value
            if value is not None: report_row[year] = value
            if diff is not None: report_row["diff"] = diff
            if nation_diff is not None: report_row["nation_diff"] = nation_diff

            report_group["rows"].append(report_row)
        report.append(report_group)
    return report


def _get_observations_from(template, surveys, year):
    def is_number(obj):
        return isinstance(obj, (int, long, float, complex))

    survey_ids = []
    previous_survey_ids = []
    for survey in surveys:
        survey_ids.append(survey.pk)
        previous_survey = survey.previous_years_survey()
        if previous_survey:
            previous_survey_ids.append(previous_survey.pk)

    observations = {}
    for key in template.all_variable_keys:
        variables = Variable.objects.filter(key=key)
        if len(variables) != 1:
            continue
        variable = variables[0]

        variables = [variable]
        if len(variable.replaces) == 1:
            variables.append(variable.replaces[0])

        observations[key] = {
            year: 0.0,
            (year - 1): 0.0,
            "total": float(OpenData.objects.filter(sample_year=year, is_active=True,
                                                   variable__in=variables).sum("value"))
        }

        value = OpenData.objects.filter(source_survey__in=survey_ids, variable__in=variables,
                                        is_active=True).sum("value")
        if is_number(value):
            observations[key][year] = value

        previous_value = OpenData.objects.filter(source_survey__in=previous_survey_ids, variable__in=variables,
                                                 is_active=True).sum("value")
        if is_number(previous_value):
            observations[key][year - 1] = previous_value

    return observations
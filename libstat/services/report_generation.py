# -*- coding: utf-8 -*-
from pprint import pprint
from libstat.models import Survey, Variable, OpenData
from libstat.report_templates import report_template_2014


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
                        "years": [year - 2, year - 1, year],
                        "rows": []}
        if group.extra is not None:
            report_group["extra"] = group.extra
        for row in group.rows:
            value0 = None
            value1 = None
            value2 = None
            total = None
            extra = None
            if row.variable_key:
                observation = observations.get(row.variable_key, {})
                value0 = observation.get(year, None)
                value1 = observation.get(year - 1, None)
                value2 = observation.get(year - 2, None)
                total = observation.get("total", None)
                if row.computation:
                    extra = row.compute(values_for(observations, row.variable_keys, year))
            elif row.variable_keys:
                value0 = row.compute(values_for(observations, row.variable_keys, year))
                value1 = row.compute(values_for(observations, row.variable_keys, year - 1))
                value2 = row.compute(values_for(observations, row.variable_keys, year - 2))

            diff = ((value0 / value1) - 1) * 100 if value0 and value1 else None
            nation_diff = (value0 / total) * 1000 if value0 and total else None

            report_row = {"label": row.description}
            if value0 is not None: report_row[year] = value0
            if value1 is not None: report_row[year - 1] = value1
            if value2 is not None: report_row[year - 2] = value2
            if diff is not None: report_row["diff"] = diff
            if nation_diff is not None: report_row["nation_diff"] = nation_diff
            if extra is not None: report_row["extra"] = extra * 100
            if row.is_sum: report_row["is_sum"] = True
            if row.label_only: report_row["label_only"] = True
            report_group["rows"].append(report_row)
        report.append(report_group)
    return report


def _get_observations_from(template, surveys, year):
    def is_number(obj):
        return isinstance(obj, (int, long, float, complex))

    survey_ids = []
    previous_survey_ids = []
    previous_previous_survey_ids = []
    for survey in surveys:
        survey_ids.append(survey.pk)
        previous_survey = survey.previous_years_survey()
        if previous_survey:
            previous_survey_ids.append(previous_survey.pk)
            previous_previous_survey = previous_survey.previous_years_survey()
            if previous_previous_survey:
                previous_previous_survey_ids.append(previous_previous_survey.pk)

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
            (year - 2): 0.0,
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

        previous_previous_value = OpenData.objects.filter(source_survey__in=previous_previous_survey_ids,
                                                          variable__in=variables, is_active=True).sum("value")
        if is_number(previous_previous_value):
            observations[key][year - 2] = previous_previous_value

    return observations
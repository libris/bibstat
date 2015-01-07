# -*- coding: utf-8 -*-
from libstat.models import Survey, Variable, OpenData
from libstat.report_templates import report_template_2014


def get_report(surveys, year):
    sigels = [sigel for survey in surveys for sigel in survey.selected_libraries]
    libraries = [survey.library for survey in Survey.objects.filter(sample_year=year, library__sigel__in=sigels)]

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
        values = []
        for key in variable_keys:
            value = observations.get(key, {}).get(year)
            values.append(float(value) if value is not None else None)
        return values

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
            incomplete_data = None
            if row.variable_key:
                observation = observations.get(row.variable_key, {})
                value0 = observation.get(year, None)
                value1 = observation.get(year - 1, None)
                value2 = observation.get(year - 2, None)
                total = observation.get("total", None)
                if row.computation:
                    extra = row.compute(values_for(observations, row.variable_keys, year))
                if observations[row.variable_key]["incomplete_data"]:
                    incomplete_data = observations[row.variable_key]["incomplete_data"]
            elif row.variable_keys:
                value0 = row.compute(values_for(observations, row.variable_keys, year))
                value1 = row.compute(values_for(observations, row.variable_keys, year - 1))
                value2 = row.compute(values_for(observations, row.variable_keys, year - 2))

            diff = ((value0 / value1) - 1) * 100 if value0 is not None and value1 else None
            if value0 == 0 and value1 == 0:
                diff = 0.0
            nation_diff = (value0 / total) * 1000 if value0 is not None and total else None
            if value0 == 0 and total == 0:
                nation_diff = 0.0

            report_row = {"label": row.description}
            if value0 is not None: report_row[year] = value0
            if value1 is not None: report_row[year - 1] = value1
            if value2 is not None: report_row[year - 2] = value2
            if diff is not None: report_row["diff"] = diff
            if nation_diff is not None: report_row["nation_diff"] = nation_diff
            if extra is not None: report_row["extra"] = extra * 100
            if incomplete_data is not None: report_row["incomplete_data"] = incomplete_data
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
        variables = [variables[0]]
        if len(variables[0].replaces) == 1:
            variables.append(variables[0].replaces[0])  # Assume only one variable is replaced

        observations[key] = {
            year: None,
            (year - 1): None,
            (year - 2): None,
            "total": float(OpenData.objects.filter(sample_year=year, is_active=True,
                                                   variable__in=variables).sum("value")),
            "incomplete_data": []
        }

        open_data = OpenData.objects.filter(source_survey__in=survey_ids, variable__in=variables,
                                            is_active=True)
        value = open_data.sum("value")
        if is_number(value) and open_data.count() != 0:
            observations[key][year] = value
        if open_data.count() < len(survey_ids):
            observations[key]["incomplete_data"].append(year)

        open_data = OpenData.objects.filter(source_survey__in=previous_survey_ids, variable__in=variables,
                                            is_active=True)
        value = open_data.sum("value")
        if is_number(value) and open_data.count() != 0:
            observations[key][year - 1] = value
        if open_data.count() < len(previous_survey_ids):
            observations[key]["incomplete_data"].append(year - 1)

        open_data = OpenData.objects.filter(source_survey__in=previous_previous_survey_ids, variable__in=variables,
                                            is_active=True)
        value = open_data.sum("value")
        if is_number(value) and open_data.count() != 0:
            observations[key][year - 2] = value
        if open_data.count() < len(previous_previous_survey_ids):
            observations[key]["incomplete_data"].append(year - 2)

    return observations
# -*- coding: utf-8 -*-
from libstat.models import Survey, Variable, OpenData
from libstat.report_templates import report_template_2014


def get_report(surveys, year):
    sigels = [sigel for survey in surveys for sigel in survey.selected_libraries]
    libraries = [survey.library for survey in Survey.objects.filter(sample_year=year, library__sigel__in=sigels)]

    # This should of course be updated when (and if) more templates are added
    report_template = report_template_2014()

    observations = pre_cache_observations(report_template, surveys, year)

    report = {
        "year": year,
        "libraries": libraries,
        "measurements": generate_report(report_template, year, observations)
    }

    return report


def generate_report(report_template, year, observations):
    def values_for(variable_keys, year):
        values = []
        for key in variable_keys:
            value = observations.get(key, {}).get(year)
            values.append(float(value) if value is not None else None)
        return values

    def group_skeleton(template_group):
        return {"title": template_group.title,
                "years": [year - 2, year - 1, year],
                "rows": [],
                "extra": template_group.extra}

    def row_skeleton(template_row):
        return {
            year: None,
            (year - 1): None,
            (year - 2): None,
            "total": None,
            "extra": None,
            "incomplete_data": None,
            "is_sum": template_row.is_sum if template_row.is_sum else None,
            "label": template_row.description,
            "label_only": template_row.label_only if template_row.label_only else None,
        }

    def clear_nones(a_dict):
        return dict([(k, v) for k, v in a_dict.iteritems() if v is not None])

    report = []
    for template_group in report_template.groups:
        group = group_skeleton(template_group)

        for template_row in template_group.rows:
            row = row_skeleton(template_row)

            if template_row.variable_key:
                observation = observations.get(template_row.variable_key, {})
                row[year] = observation.get(year, None)
                row[year - 1] = observation.get(year - 1, None)
                row[year - 2] = observation.get(year - 2, None)
                row["total"] = observation.get("total", None)
                row["incomplete_data"] = observations.get(template_row.variable_key, {}).get("incomplete_data", None)
                if template_row.computation:
                    row["extra"] = template_row.compute(values_for(template_row.variable_keys, year))
                    row["extra"] = row["extra"] * 100 if row["extra"] is not None else None

            elif template_row.variable_keys:
                row[year] = template_row.compute(values_for(template_row.variable_keys, year))
                row[year - 1] = template_row.compute(values_for(template_row.variable_keys, year - 1))
                row[year - 2] = template_row.compute(values_for(template_row.variable_keys, year - 2))

            if row[year] == 0 and row[year - 1] == 0:
                row["diff"] = 0.0
            elif row[year] is not None and row[year - 1]:
                row["diff"] = ((row[year] / row[year - 1]) - 1) * 100

            if row[year] == 0 and row[year - 1] == 0:
                row["nation_diff"] = 0.0
            elif row[year] is not None and row["total"]:
                row["nation_diff"] = (row[year] / row["total"]) * 1000

            row["total"] = None
            group["rows"].append(clear_nones(row))
        report.append(clear_nones(group))
    return report


def pre_cache_observations(template, surveys, year):
    def is_number(obj):
        return isinstance(obj, (int, long, float, complex))

    def survey_ids_three_latest_years():
        survey_ids = {
            year: [],
            (year - 1): [],
            (year - 2): []
        }

        for survey in surveys:
            survey_ids[year].append(survey.pk)
            previous_survey = survey.previous_years_survey()
            if previous_survey:
                survey_ids[year - 1].append(previous_survey.pk)
                previous_previous_survey = previous_survey.previous_years_survey()
                if previous_previous_survey:
                    survey_ids[year - 2].append(previous_previous_survey.pk)
        return survey_ids

    def observation_skeleton(variables):
        return {
            year: None,
            (year - 1): None,
            (year - 2): None,
            "incomplete_data": [],
            "total": float(OpenData.objects.filter(sample_year=year, is_active=True,
                                                   variable__in=variables).sum("value"))
        }

    survey_ids = survey_ids_three_latest_years()

    observations = {}
    for key in template.all_variable_keys:
        variables = [Variable.objects.get(key=key)]
        if len(variables[0].replaces) == 1:
            variables.append(variables[0].replaces[0])  # Assume only one variable is replaced

        observations[key] = observation_skeleton(variables)

        for y in (year, year - 1, year - 2):
            open_data = OpenData.objects.filter(source_survey__in=survey_ids[y], variable__in=variables,
                                                is_active=True)
            value = open_data.sum("value")
            if is_number(value) and open_data.count() != 0:
                observations[key][y] = value
            if open_data.count() < len(survey_ids[y]):
                observations[key]["incomplete_data"].append(y)

    return observations
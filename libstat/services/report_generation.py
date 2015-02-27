# -*- coding: utf-8 -*-
from pprint import pprint
import uuid

from libstat.models import Survey, Variable, OpenData, CachedReport
from libstat.report_templates import report_template_2014


REPORT_CACHE_LIMIT = 500


def get_cached_report(surveys, year):
    if (CachedReport.objects.count() != 0 and
            ((OpenData.objects.count() != 0
              and OpenData.objects.first().date_modified > CachedReport.objects.first().date_created) or
                 (Variable.objects.count() != 0 and Variable.objects.all().order_by("-date_modified").first().date_modified > CachedReport.objects.first().date_created))):
        CachedReport.drop_collection()

    reports = CachedReport.objects.filter(surveys__all=surveys, surveys__size=len(surveys), year=str(year))
    report = reports[0].report if reports.count() == 1 else None

    return report


def store_cached_report(report, surveys, year):
    if not get_cached_report(surveys, year):
        cached_report = CachedReport(report=report, surveys=surveys, year=str(year))
        cached_report.save()
    CachedReport.objects[REPORT_CACHE_LIMIT:].filter().delete()


def get_report(surveys, year):
    cached_report = get_cached_report(surveys, year)

    if cached_report:
        return cached_report
    else:
        # This should of course be updated when (and if) more templates are added
        report_template = report_template_2014()

        observations = pre_cache_observations(report_template, surveys, year)

        sigels = [sigel for survey in surveys for sigel in survey.selected_libraries]
        libraries = [survey.library for survey in Survey.objects.filter(sample_year=year, library__sigel__in=sigels)]

        def sort_key(library):
            return library.name.lower()

        libraries.sort(key=sort_key)

        report = {
            "id": str(uuid.uuid1()),
            "year": year,
            "libraries": [
                {
                    "sigel": library.sigel,
                    "name": library.name,
                    "address": library.address,
                    "city": library.city
                } for library in libraries],
            "measurements": generate_report(report_template, year, observations)
        }

        store_cached_report(report, surveys, year)

        return report


def generate_report(report_template, year, observations):
    year0 = str(year)
    year1 = str(year - 1)
    year2 = str(year - 2)

    def values_for(variable_keys, year):
        values = []
        for key in variable_keys:
            value = observations.get(key, {}).get(year)
            values.append(float(value) if value is not None else None)
        return values

    def group_skeleton(template_group):
        return {
            "title": template_group.title,
            "years": [year2, year1, year0],
            "rows": [],
            "extra": template_group.extra,
            "show_chart": template_group.show_chart
        }

    def row_skeleton(template_row):
        return {
            year0: None,
            year1: None,
            year2: None,
            "total": None,
            "extra": None,
            "incomplete_data": [],
            "description": template_row.explanation,
            "show_in_chart": template_row.show_in_chart if template_row.variable_key else False,
            "is_key_figure": None,
            "is_sum": template_row.is_sum if template_row.is_sum else None,
            "label": template_row.description,
            "label_only": template_row.label_only if template_row.label_only else None,
            "percentage": template_row.percentage if template_row.percentage else None
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
                row[year0] = observation.get(year, None)
                row[year1] = observation.get(year - 1, None)
                row[year2] = observation.get(year - 2, None)
                row["total"] = observation.get("total", None)
                row["incomplete_data"] = observations.get(template_row.variable_key, {}).get("incomplete_data", None)
                if template_row.computation:
                    row["extra"] = template_row.compute(values_for(template_row.variable_keys, year))
                    row["extra"] = row["extra"] * 100 if row["extra"] is not None else None

            elif template_row.variable_keys:
                row["is_key_figure"] = True
                for y in (year0, year1, year2):
                    row[y] = template_row.compute(values_for(template_row.variable_keys, int(y)))
                    for key in template_row.variable_keys:
                        if int(y) in observations.get(key, {}).get("incomplete_data", []) and int(y) not in row[
                            "incomplete_data"]:
                            row["incomplete_data"].append(int(y))

            if row[year0] == 0 and row[year1] == 0:
                row["diff"] = 0.0
            elif row[year0] is not None and row[year1]:
                row["diff"] = ((row[year0] / row[year1]) - 1) * 100

            if row[year0] == 0 and row[year1] == 0:
                row["nation_diff"] = 0.0
            elif row[year0] is not None and row["total"]:
                row["nation_diff"] = (row[year0] / row["total"]) * 1000

            row["incomplete_data"] = [str(a) for a in row["incomplete_data"]] if row["incomplete_data"] else None

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
        try:
            total = float(OpenData.objects.filter(sample_year=year, is_active=True, variable__in=variables).sum("value"))
        except Exception as e:
            total = None
        returns = {
            year: None,
            (year - 1): None,
            (year - 2): None,
            "incomplete_data": [],
            "total": total
        }
        return returns

    survey_ids = survey_ids_three_latest_years()

    observations = {}
    for key in template.all_variable_keys:
        variables = Variable.objects.filter(key=key)
        if variables.count() != 1:
            continue
        variables = [variables[0]]

        if len(variables[0].replaces) > 0:
            library_types = [target_group for variable in variables[0].replaces for target_group in variable.target_groups]
            if len(library_types) == len(set(library_types)):
                    variables += variables[0].replaces

        observations[key] = observation_skeleton(variables)

        for y in (year, year - 1, year - 2):
            open_data = OpenData.objects.filter(source_survey__in=survey_ids[y], variable__in=variables,
                                                is_active=True)
            value = open_data.sum("value")
            if is_number(value) and open_data.count() != 0:
                observations[key][y] = float(value)
            if open_data.count() < len(survey_ids[y]):
                observations[key]["incomplete_data"].append(y)

    return observations
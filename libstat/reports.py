# -*- coding: utf-8 -*-
from libstat.models import Survey, Variable


class ReportTemplate():
    def __init__(self, groups):
        self.groups = groups


class Group():
    def __init__(self, title, rows):
        self.title = title
        self.rows = rows


class VariableRow():
    def __init__(self, variable_key, description=None):
        if description:
            self.description = description
        else:
            self.description = Variable.objects.get(key=variable_key).question_part
        self.variable_key = variable_key


class KeyFigureRow():
    def __init__(self, description, computation, variable_keys):
        self.description = description
        self.computation = computation
        self.variable_keys = variable_keys


def generate_report(template, sample_year, observations):
    report = []
    for group in template.groups:
        report_group = [[group.title, sample_year - 1, sample_year]]
        for row in group.rows:
            report_row = []
            if isinstance(row, VariableRow):
                report_row = [row.description,
                              observations.get(row.variable_key, {}).get(sample_year - 1, None),
                              observations.get(row.variable_key, {}).get(sample_year, None)]
            elif isinstance(row, KeyFigureRow):
                values = [observations.get(key, {}).get(sample_year, None) for key in row.variable_keys]
                values = [float(v) if v is not None else None for v in values]
                previous_values = [observations.get(key, {}).get(sample_year - 1, None) for key in row.variable_keys]
                previous_values = [float(v) if v is not None else None for v in previous_values]
                if None not in values:
                    try:
                        value = apply(row.computation, values)
                    except ZeroDivisionError:
                        value = None
                else:
                    value = None
                if None not in previous_values:
                    try:
                        previous_value = apply(row.computation, previous_values)
                    except ZeroDivisionError:
                        previous_value = None
                else:
                    previous_value = None
                report_row = [row.description, previous_value, value]
            report_group.append(report_row)
        report.append(report_group)
    return report


def get_report(surveys, year):
    def is_number(obj):
        return isinstance(obj, (int, long, float, complex))

    previous_year = year - 1

    surveys = [(survey, survey.previous_years_survey()) for survey in surveys]
    libraries = []
    for survey, _ in surveys:
        for sigel in survey.selected_libraries:
            library = Survey.objects.get(sample_year=year, library__sigel=sigel).library
            libraries.append({
                "sigel": library.sigel,
                "name": library.name
            })

    observations = {}
    for survey, previous_survey in surveys:
        for observation in survey.observations:
            if is_number(observation.value):
                variable_key = observation.variable.key
                if variable_key not in observations:
                    observations[variable_key] = {
                        year: 0,
                        previous_year: 0
                    }
                observations[variable_key][year] += float(observation.value)
            previous_value = survey.previous_years_value(observation.variable, previous_years_survey=previous_survey)
            if is_number(previous_value):
                variable_key = observation.variable.key
                if variable_key not in observations:
                    observations[variable_key] = {
                        year: 0,
                        previous_year: 0
                    }
                observations[variable_key][previous_year] += float(previous_value)

    report = {
        "year": year,
        "libraries": libraries,
        "measurements": generate_report(report_template_2014(), year, observations)
    }

    return report


def report_template_2014():
    return ReportTemplate(groups=[
        Group(title=u"Organisation",
              rows=[VariableRow(description=u"Antal bemannade serviceställen",
                                variable_key=u"BemanService01"),
                    VariableRow(description=u"",
                                variable_key=u"Integrerad01"),
                    VariableRow(description=u"",
                                variable_key=u"Obeman01"),
                    VariableRow(description=u"",
                                variable_key=u"ObemanLan01"),
                    VariableRow(description=u"",
                                variable_key=u"Bokbuss01"),
                    VariableRow(description=u"",
                                variable_key=u"BokbussHP01"),
                    VariableRow(description=u"",
                                variable_key=u"Bokbil01"),
                    VariableRow(description=u"",
                                variable_key=u"Population01"),
                    # VariableRow(description=u"",
                    #             variable_key=u"Population02"),
                    # VariableRow(description=u"",
                    #             variable_key=u"Population03"),
                    KeyFigureRow(description=u"Antal bemannade serviceställen per 1000 invånare",
                                 computation=(lambda a, b: a / (b / 1000)),
                                 variable_keys=[u"BemanService01", u"Population01"]),
                    KeyFigureRow(description=u"Antal integrerade serviceställen",
                                 computation=(lambda a, b: a / b),
                                 variable_keys=[u"Integrerad01", u"BemanService01"]),
                    KeyFigureRow(
                        description=u"Medelantal utlån per servicesställe där vidare låneregistrering inte sker",
                        computation=(lambda a, b: a / b),
                        variable_keys=[u"ObemanLan01", u"Obeman01"])
              ])
    ])

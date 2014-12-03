# -*- coding: utf-8 -*-

class ReportTemplate():
    def __init__(self, groups):
        self.groups = groups


class Group():
    def __init__(self, title, rows):
        self.title = title
        self.rows = rows


class VariableRow():
    def __init__(self, description, variable_key):
        self.description = description
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
                report_row = [row.description,
                              apply(row.computation, previous_values) if None not in previous_values else None,
                              apply(row.computation, values) if None not in values else None]
            report_group.append(report_row)
        report.append(report_group)
    return report


def get_report(surveys, year):
    previous_year = year - 1
    observations = {}
    for survey, previous_survey in surveys:
        for observation in survey.observations:
            variable_key = observation.variable.key
            if variable_key not in observations:
                observations[variable_key] = {
                    year: 0,
                    previous_year: 0
                }
            observations[variable_key][year] += observation.value
        for observation in previous_survey.observations:
            variable_key = observation.variable.key
            if variable_key not in observations:
                observations[variable_key] = {
                    year: 0,
                    previous_year: 0
                }
            observations[variable_key][previous_year] += observation.value
    return generate_report(report_template_2014, year, observations)


report_template_2014 = ReportTemplate(groups=[
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
                VariableRow(description=u"",
                            variable_key=u"Population02"),
                VariableRow(description=u"",
                            variable_key=u"Population03"),
                KeyFigureRow(description=u"Antal bemannade serviceställen per 1000 invånare",
                             computation=(lambda a, b: a / (b / 1000)),
                             variable_keys=[u"BemanService01", u"Population01"]),
                KeyFigureRow(description=u"Antal integrerade serviceställen",
                             computation=(lambda a, b: a / b),
                             variable_keys=[u"Integrerad01", u"BemanService01"]),
                KeyFigureRow(description=u"Medelantal utlån per servicesställe där vidare låneregistrering inte sker",
                             computation=(lambda a, b: a / b),
                             variable_keys=[u"ObemanLan01", u"Obeman01"])
          ])
])

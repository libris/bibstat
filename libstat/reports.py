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
        if description is not None:
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
              rows=[VariableRow(variable_key=u"BemanService01"),
                    VariableRow(variable_key=u"Integrerad01"),
                    VariableRow(variable_key=u"Obeman01"),
                    VariableRow(variable_key=u"ObemanLan01"),
                    VariableRow(variable_key=u"Bokbuss01"),
                    VariableRow(variable_key=u"BokbussHP01"),
                    VariableRow(variable_key=u"Bokbil01"),
                    VariableRow(variable_key=u"Population01"),
                    # VariableRow(variable_key=u"Population02"),
                    # VariableRow(variable_key=u"Population03"),
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
              ]),
        Group(title=u"Årsverken",
              rows=[
                  VariableRow(variable_key=u"Arsverke01"),
                  VariableRow(variable_key=u"Arsverke02"),
                  VariableRow(variable_key=u"Arsverke03"),
                  VariableRow(variable_key=u"Arsverke04"),
                  VariableRow(variable_key=u"Arsverke99"),
                  VariableRow(variable_key=u"Arsverke05"),
                  KeyFigureRow(description=u"Andel årsverken för barn och unga",
                               computation=(lambda a, b: a / b),
                               variable_keys=[u"Arsverke05", u"Arsverke99"]),
                  KeyFigureRow(description=u"Andel åreverken med bibliotekariekompetens",
                               computation=(lambda a, b: a / b),
                               variable_keys=[u"Arsverke01", u"Arsverke99"]),
                  KeyFigureRow(description=u"Antal  årsverken per 1000 invånare",
                               computation=(lambda a, b: a / b),
                               variable_keys=[u"Arsverke99", u"Population01"]),
                  KeyFigureRow(description=u"Antal årsverken per personer i målgruppen",
                               computation=(lambda a, b: a / b),
                               variable_keys=[u"Arsverke99", u"Population02"]),
                  KeyFigureRow(description=u"Antal fysiska besök per årsverke",
                               computation=(lambda a, b: a / b),
                               variable_keys=[u"Besok01", u"Arsverke99"]),
                  KeyFigureRow(description=u"Antal aktiva låntagare per årsverke",
                               computation=(lambda a, b: a / b),
                               variable_keys=[u"Aktiv99", u"Arsverke99"]),
              ]),
        Group(title=u"Personal",
              rows=[
                  VariableRow(variable_key=u"Personer01"),
                  VariableRow(variable_key=u"Personer02"),
                  VariableRow(variable_key=u"Personer99"),
                  KeyFigureRow(description=u"Andel anställda kvinnor",
                               computation=(lambda a, b: a / b ),
                               variable_keys=[u"Personer01", u"Personer99"]),
                  KeyFigureRow(description=u"Antal årsverken per person",
                               computation=(lambda a, b: a / b ),
                               variable_keys=[u"Arsverke99", u"Personer99"]),
              ]),
        Group(title=u"Ekonomi",
              rows=[
                  VariableRow(variable_key=u"Utgift01"),
                  VariableRow(variable_key=u"Utgift02"),
                  VariableRow(variable_key=u"Utgift03"),
                  VariableRow(variable_key=u"Utgift04"),
                  VariableRow(variable_key=u"Utgift05"),
                  VariableRow(variable_key=u"Utgift06"),
                  VariableRow(variable_key=u"Utgift99"),
                  VariableRow(variable_key=u"Utgift07"),
                  KeyFigureRow(description=u"Mediekostnad per invånare",
                               computation=(lambda a, b, c: (a + b) / c ),
                               variable_keys=[u"Utgift01", u"Utgift02", u"Population01"]),
                  KeyFigureRow(description=u"Mediekostnad per personer i målgruppen",
                               computation=(lambda a, b, c: (a + b) / c ),
                               variable_keys=[u"Utgift01", u"Utgift02", u"Population01"]),
                  KeyFigureRow(description=u"Total driftkostnad per invånare",
                               computation=(lambda a, b: a / b ),
                               variable_keys=[u"Utgift99", u"Population01"]),
                  KeyFigureRow(description=u"Total driftkostnad per personer i målgruppen",
                               computation=(lambda a, b: a / b ),
                               variable_keys=[u"Utgift99", u"Population02"]),
                  KeyFigureRow(description=u"Andel kostnader för medier av total driftkostnad",
                               computation=(lambda a, b, c: (a + b) / c ),
                               variable_keys=[u"Utgift01", u"Utgift02", u"Utgift98"]),
                  KeyFigureRow(description=u"Andel kostnader för personal av total driftkostnader",
                               computation=(lambda a, b, c: (a + b) / c ),
                               variable_keys=[u"Utgift03", u"Utgift04", u"Utgift99"]),
                  KeyFigureRow(description=u"Andel kostnad för e-medier av totala driftskostnader",
                               computation=(lambda a, b, c: a / (b + c) ),
                               variable_keys=[u"Utgift02", u"Utgift01", u"Utgift02"]),
              ]),
        Group(title=u"Egengenererade intäkter",
              rows=[
                  VariableRow(variable_key=u"Intakt01"),
                  VariableRow(variable_key=u"Intakt02"),
                  VariableRow(variable_key=u"Intakt03"),
                  VariableRow(variable_key=u"Intakt99"),
                  KeyFigureRow(
                      description=u"Andel egengenererade intäkter i förhållande till de totala driftskostnaderna",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Intakt99", u"Utgift99"])
              ]),
        Group(title=u"Fysiskt bestånd",
              rows=[
                  VariableRow(variable_key=u"Bestand101"),
                  VariableRow(variable_key=u"Bestand102"),
                  VariableRow(variable_key=u"Bestand103"),
                  VariableRow(variable_key=u"Bestand104"),
                  VariableRow(variable_key=u"Bestand105"),
                  VariableRow(variable_key=u"Bestand106"),
                  VariableRow(variable_key=u"Bestand107"),
                  VariableRow(variable_key=u"Bestand108"),
                  VariableRow(variable_key=u"Bestand109"),
                  VariableRow(variable_key=u"Bestand110"),
                  VariableRow(variable_key=u"Bestand111"),
                  VariableRow(variable_key=u"Bestand112"),
                  VariableRow(variable_key=u"Bestand113"),
                  VariableRow(variable_key=u"Bestand199"),
                  KeyFigureRow(description=u"Totalt fysiskt mediebestånd per invånare",
                               computation=(lambda a, b: a / b),
                               variable_keys=[u"Bestand199", u"Population01"]),
                  KeyFigureRow(description=u"Antal  tryckta böcker per invånare i beståndet",
                               computation=(lambda a, b: a / b),
                               variable_keys=[u"Bestand101", u"Population01"])
              ]),
        Group(title=u"Fysiskt nyförvärv",
              rows=[
                  VariableRow(variable_key=u"Bestand201"),
                  VariableRow(variable_key=u"Bestand202"),
                  VariableRow(variable_key=u"Bestand203"),
                  VariableRow(variable_key=u"Bestand204"),
                  VariableRow(variable_key=u"Bestand205"),
                  VariableRow(variable_key=u"Bestand206"),
                  VariableRow(variable_key=u"Bestand207"),
                  VariableRow(variable_key=u"Bestand208"),
                  VariableRow(variable_key=u"Bestand209"),
                  VariableRow(variable_key=u"Bestand210"),
                  VariableRow(variable_key=u"Bestand211"),
                  VariableRow(variable_key=u"Bestand212"),
                  VariableRow(variable_key=u"Bestand213"),
                  VariableRow(variable_key=u"Bestand299"),
                  KeyFigureRow(description=u"Antal fysiska  nyförvärv per 1000 invånare (ej tidn.tidskr.)",
                               computation=(lambda a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11:
                                            (a1 + a2 + a3 + a4 + a5 + a6 + a7 + a8 + a9 + a10) / (a11 / 1000)),
                               variable_keys=[u"Bestand101", u"Bestand103", u"Bestand104", u"Bestand107", u"Bestand108",
                                              u"Bestand109", u"Bestand110", u"Bestand111", u"Bestand112", u"Bestand113",
                                              u"Population01"])
              ]),
        Group(title=u"Elektroniskt titelbestånd",
              rows=[
                  VariableRow(variable_key=u"Bestand301"),
                  VariableRow(variable_key=u"Bestand302"),
                  VariableRow(variable_key=u"Bestand303"),
                  VariableRow(variable_key=u"Bestand304"),
                  VariableRow(variable_key=u"Bestand305"),
                  VariableRow(variable_key=u"Bestand306"),
                  VariableRow(variable_key=u"Bestand307"),
                  VariableRow(variable_key=u"Bestand308"),
                  VariableRow(variable_key=u"Bestand310"),
                  VariableRow(variable_key=u"Bestand311"),
                  VariableRow(variable_key=u"Bestand312"),
                  VariableRow(variable_key=u"Bestand313"),
                  VariableRow(variable_key=u"Bestand399"),
                  KeyFigureRow(description=u"Andel e-bokstitlar av det totala elektroniska titelbeståndet",
                               computation=(lambda a, b: a/b),
                               variable_keys=[u"Bestand301", u"Bestand399"])
              ]),

    ])

# -*- coding: utf-8 -*-
from pprint import pprint
from libstat.models import Survey, Variable, OpenData


class ReportTemplate():
    @property
    def all_variable_keys(self):
        variable_keys = []
        for group in self.groups:
            for row in group.rows:
                if isinstance(row, VariableRow):
                    variable_keys.append(row.variable_key)
                elif isinstance(row, KeyFigureRow):
                    for variable_key in row.variable_keys:
                        variable_keys.append(variable_key)
        return variable_keys

    def __init__(self, *args, **kwargs):
        self.groups = kwargs.pop("groups", None)


class Group():
    def __init__(self, *args, **kwargs):
        self.title = kwargs.pop("title", None)
        self.rows = kwargs.pop("rows", None)


class VariableRow():
    def __init__(self, *args, **kwargs):
        self.variable_key = kwargs.pop("variable_key", None)
        self.description = kwargs.pop("description", None)
        if self.description is None:
            variables = Variable.objects.filter(key=self.variable_key)
            self.description = variables[0].question_part if len(variables) == 1 else None


class KeyFigureRow():
    def compute(self, values):
        if None in values:
            return None
        try:
            return apply(self.computation, values)
        except ZeroDivisionError:
            return None

    def __init__(self, *args, **kwargs):
        self.description = kwargs.pop("description", None)
        self.computation = kwargs.pop("computation", None)
        self.variable_keys = kwargs.pop("variable_keys", None)


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


def get_report(surveys, year):
    libraries = []
    for survey in surveys:
        for sigel in survey.selected_libraries:
            libraries.append(Survey.objects.get(sample_year=year, library__sigel=sigel).library)

    template = report_template_2014()

    observations = _get_observations_from(template, surveys, year)

    report = {
        "year": year,
        "libraries": libraries,
        "measurements": generate_report(template, year, observations)
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
                               computation=(lambda a, b: a / b),
                               variable_keys=[u"Bestand301", u"Bestand399"])
              ]),

    ])

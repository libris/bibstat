# -*- coding: utf-8 -*-
from libstat.models import Variable


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


def report_template_2014():
    return ReportTemplate(groups=[
        Group(title=u"Organisation",
              rows=[
                  VariableRow(variable_key=u"BemanService01"),
                  VariableRow(variable_key=u"Integrerad01"),
                  VariableRow(variable_key=u"Obeman01"),
                  VariableRow(variable_key=u"ObemanLan01"),
                  VariableRow(variable_key=u"Bokbuss01"),
                  VariableRow(variable_key=u"BokbussHP01"),
                  VariableRow(variable_key=u"Bokbil01"),
                  VariableRow(variable_key=u"Population01"),
                  VariableRow(variable_key=u"Population02"),
                  VariableRow(variable_key=u"Population03"),
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
                               computation=(lambda a, b: a / b),
                               variable_keys=[u"Personer01", u"Personer99"]),
                  KeyFigureRow(description=u"Antal årsverken per person",
                               computation=(lambda a, b: a / b),
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
                               computation=(lambda a, b, c: (a + b) / c),
                               variable_keys=[u"Utgift01", u"Utgift02", u"Population01"]),
                  KeyFigureRow(description=u"Mediekostnad per personer i målgruppen",
                               computation=(lambda a, b, c: (a + b) / c),
                               variable_keys=[u"Utgift01", u"Utgift02", u"Population01"]),
                  KeyFigureRow(description=u"Total driftkostnad per invånare",
                               computation=(lambda a, b: a / b),
                               variable_keys=[u"Utgift99", u"Population01"]),
                  KeyFigureRow(description=u"Total driftkostnad per personer i målgruppen",
                               computation=(lambda a, b: a / b),
                               variable_keys=[u"Utgift99", u"Population02"]),
                  KeyFigureRow(description=u"Andel kostnader för medier av total driftkostnad",
                               computation=(lambda a, b, c: (a + b) / c),
                               variable_keys=[u"Utgift01", u"Utgift02", u"Utgift98"]),
                  KeyFigureRow(description=u"Andel kostnader för personal av total driftkostnader",
                               computation=(lambda a, b, c: (a + b) / c),
                               variable_keys=[u"Utgift03", u"Utgift04", u"Utgift99"]),
                  KeyFigureRow(description=u"Andel kostnad för e-medier av totala driftskostnader",
                               computation=(lambda a, b, c: a / (b + c)),
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

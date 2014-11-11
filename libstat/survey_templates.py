# -*- coding: utf-8 -*-
from libstat.models import Section, Group, Cell, Row, SurveyTemplate


def _default_template_from_survey_response(response):
    rows = []
    for observation in response.observations:
        variable = observation.variable
        rows.append(Row(cells=[Cell(variable_key=variable.key, types=["text"])]))

    return SurveyTemplate(
        sections=[
            Section(
                title="",
                groups=[
                    Group(
                        rows=rows
                    )
                ]
            )
        ]
    )


def _survey_template_2014():
    return SurveyTemplate(
        key="",
        target_year="",
        organization_name="",
        municipality="",
        municipality_code="",
        head_authority="",
        respondent_name="",
        respondent_email="",
        respondent_phone="",
        website="",
        sections=[
            Section(
                title=u"Frågor om biblioteksorganisationen",
                groups=[
                    Group(
                        rows=[
                            Row(
                                cells=[Cell(variable_key=u"Namn01", types=["text"])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Epost01", types=['email', 'required'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Tele01", types=["text"])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Plan01", types=["text"])]
                            )
                        ]
                    ),
                    # TODO Välja bibliotek (5)
                    Group(
                        rows=[
                            Row(
                                cells=[Cell(variable_key=u"BemanService01", types=['required', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Integrerad01", types=['required', 'integer'])]
                            )
                        ]
                    ),
                    Group(
                        rows=[
                            Row(
                                cells=[Cell(variable_key=u"Obeman01", types=['required', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"ObemanLan01", types=['required', 'integer'])]
                            )
                        ]
                    ),
                    Group(
                        rows=[
                            Row(
                                cells=[Cell(variable_key=u"Bokbuss01", types=['required', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"BokbussHP01", types=['required', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Bokbil01", types=['integer'])]
                            )
                        ]
                    ),
                    Group(
                        rows=[
                            Row(
                                cells=[Cell(variable_key=u"Population01", types=['integer'])]
                            )
                        ]
                    ),
                ]
            ),
            Section(
                title=u"Frågor om bemanning och personal",
                groups=[
                    Group(
                        rows=[
                            Row(
                                cells=[Cell(variable_key=u"Arsverke01", types=['sum', 'numeric'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Arsverke02", types=['sum', 'numeric'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Arsverke03", types=['sum', 'numeric'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Arsverke04", types=['sum', 'numeric'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Arsverke99", types=['sum', 'numeric'],
                                            sum_of=["Arsverke01", "Arsverke02", "Arsverke03", "Arsverke04"])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Arsverke05", types=['required', 'numeric'])]
                            )
                        ]
                    ),
                    Group(
                        rows=[
                            Row(
                                cells=[Cell(variable_key=u"Personer01", types=['sum', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Personer02", types=['sum', 'integer'])]
                            ),
                            Row(
                                cells=[
                                    Cell(variable_key=u"Personer99", types=['sum', 'integer'],
                                         sum_of=[u"Personer01", u"Personer02"])]
                            )
                        ]
                    ),
                    Group(
                        rows=[
                            Row(
                                cells=[
                                    Cell(variable_key=u"Personkomm", types=["comment"])
                                ]
                            )
                        ]
                    )
                ]
            ),
            Section(
                title=u"Frågor om ekonomi",
                groups=[
                    Group(
                        rows=[
                            Row(
                                cells=[Cell(variable_key=u"Utgift01", types=['sum', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Utgift02", types=['sum', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Utgift03", types=['sum', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Utgift04", types=['sum', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Utgift05", types=['sum', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Utgift06", types=['sum', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Utgift99", types=['sum', 'integer'],
                                            sum_of=[u"Utgift01", u"Utgift02", u"Utgift03", u"Utgift04", u"Utgift05",
                                                    u"Utgift06"])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Utgift07", types=['integer'])]
                            )
                        ]
                    ),
                    Group(
                        rows=[
                            Row(
                                cells=[Cell(variable_key=u"Intakt01", types=['sum', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Intakt02", types=['sum', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Intakt03", types=['sum', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Intakt99", types=['sum', 'integer'],
                                            sum_of=[u"Intakt01", u"Intakt02", u"Intakt03"])]
                            ),
                        ]
                    ),
                    Group(
                        rows=[
                            Row(
                                cells=[
                                    Cell(variable_key=u"Ekonomikomm", types=["comment"])
                                ]
                            )
                        ]
                    )
                ]
            ),
            Section(
                title=u"Bestånd – nyförvärv",
                groups=[
                    Group(
                        rows=[
                            Row(
                                cells=[
                                    Cell(variable_key=u"Bestand101", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand201", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand301", types=['sum', 'integer'])
                                ]
                            ),
                            Row(
                                cells=[
                                    Cell(variable_key=u"Bestand102", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand202", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand302", types=['sum', 'integer']),
                                ]
                            ),
                            Row(
                                cells=[
                                    Cell(variable_key=u"Bestand103", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand203", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand303", types=['sum', 'integer'])
                                ]
                            ),
                            Row(
                                cells=[
                                    Cell(variable_key=u"Bestand104", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand204", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand304", types=['sum', 'integer'])
                                ]
                            ),
                            Row(
                                cells=[
                                    Cell(variable_key=u"Bestand105", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand205", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand305", types=['sum', 'integer'])
                                ]
                            ),
                            Row(
                                cells=[
                                    Cell(variable_key=u"Bestand106", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand206", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand306", types=['sum', 'integer'])
                                ]
                            ),
                            Row(
                                cells=[
                                    Cell(variable_key=u"Bestand107", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand207", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand307", types=['sum', 'integer'])
                                ]
                            ),
                            Row(
                                cells=[
                                    Cell(variable_key=u"Bestand108", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand208", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand308", types=['sum', 'integer'])
                                ]
                            ),
                            Row(
                                cells=[
                                    Cell(variable_key=u"Bestand109", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand209", types=['sum', 'integer'])
                                ]
                            ),
                            Row(
                                cells=[
                                    Cell(variable_key=u"Bestand110", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand210", types=['sum', 'integer']),
                                    Cell(variable_key=u"Bestand310", types=['sum', 'integer'])
                                ]
                            ),
                            Row(
                                cells=[
                                    Cell(variable_key=u"Bestand199", types=['sum', 'integer'],
                                         sum_of=['Bestand101', 'Bestand102', 'Bestand103', 'Bestand104', 'Bestand105',
                                                 'Bestand106', 'Bestand107', 'Bestand108', 'Bestand109', 'Bestand110',
                                                 'Bestand111', 'Bestand112', 'Bestand113']),
                                    Cell(variable_key=u"Bestand299", types=['sum', 'integer'],
                                         sum_of=['Bestand201', 'Bestand202', 'Bestand203', 'Bestand204', 'Bestand205',
                                                 'Bestand206', 'Bestand207', 'Bestand208', 'Bestand209', 'Bestand210',
                                                 'Bestand211', 'Bestand212', 'Bestand213']),
                                    Cell(variable_key=u"Bestand399", types=['sum', 'integer'],
                                         sum_of=['Bestand301', 'Bestand302', 'Bestand303', 'Bestand304', 'Bestand305',
                                                 'Bestand306', 'Bestand307', 'Bestand308', 'Bestand310', 'Bestand311',
                                                 'Bestand312', 'Bestand313'])
                                ]
                            )
                        ]
                    ),
                    Group(
                        rows=[
                            Row(
                                cells=[Cell(variable_key=u"Barn01", types=['required', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Barn02", types=['required', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Barn03", types=['required', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"HCG04", types=['required', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"Ref05", types=['required', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"LasnedBest01", types=['required', 'integer'])]
                            ),
                            Row(
                                cells=[Cell(variable_key=u"LasnedUtlan01", types=['required', 'integer'])]
                            ),
                        ]
                    ),
                    Group(
                        rows=[
                            Row(
                                cells=[
                                    Cell(variable_key=u"Titlar101", types=["sum", "integer"]),
                                    Cell(variable_key=u"Titlar102", types=["sum", "integer"]),
                                    Cell(variable_key=u"Titlar199", types=["sum", "integer"],
                                         sum_of=[u"Titlar101", u"Titlar102"]),
                                ]
                            ),
                            Row(
                                cells=[
                                    Cell(variable_key=u"Titlar201", types=["sum", "integer"]),
                                    Cell(variable_key=u"Titlar202", types=["sum", "integer"]),
                                    Cell(variable_key=u"Titlar299", types=["sum", "integer"],
                                         sum_of=[u"Titlar201", u"Titlar202"]),
                                ]
                            ),
                            Row(
                                cells=[
                                    Cell(variable_key=u"Titlar301", types=["sum", "integer"]),
                                    Cell(variable_key=u"Titlar302", types=["sum", "integer"]),
                                    Cell(variable_key=u"Titlar399", types=["sum", "integer"],
                                         sum_of=[u"Titlar301", u"Titlar302"]),
                                ]
                            ),
                            Row(
                                cells=[
                                    Cell(variable_key=u"Titlar497", types=["sum", "integer"]),
                                    Cell(variable_key=u"Titlar498", types=["sum", "integer"]),
                                    Cell(variable_key=u"Titlar499", types=["sum", "integer"],
                                         sum_of=[u"Titlar497", u"Titlar498"]),
                                ]
                            )
                        ]
                    )
                ]
            ),
        ]
    )


def survey_template(year, response=None):
    if year == 2014:
        return _survey_template_2014()
    return _default_template_from_survey_response(response)

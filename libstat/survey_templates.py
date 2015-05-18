# -*- coding: utf-8 -*-
from libstat.models import Section, Group, Cell, Row, SurveyTemplate


def _survey_template_2014():
    return SurveyTemplate(
        intro_text_variable_key="Introtext2014",
        sections=[
            Section(title=u"Frågor om biblioteksorganisationen",
                    groups=[
                        Group(rows=[
                            #TODO: remove types and user variable type instead
                            Row(cells=[Cell(variable_key=u"Namn01")]),#text
                            Row(cells=[Cell(variable_key=u"Epost01", required=True)]),#email
                            Row(cells=[Cell(variable_key=u"Tele01")]),#text
                            Row(cells=[Cell(variable_key=u"Plan01")])]),#text
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"BemanService01", required=True)]),#integer
                            Row(cells=[Cell(variable_key=u"Integrerad01", required=True)])]),#integer
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Obeman01", required=True)]),#integer
                            Row(cells=[Cell(variable_key=u"ObemanLan01", required=True)])]),#integer
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Bokbuss01", required=True)]),#integer
                            Row(cells=[Cell(variable_key=u"BokbussHP01", required=True)]),#integer
                            Row(cells=[Cell(variable_key=u"Bokbil01")])]),#integer
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Population01")]),#integer
                            Row(cells=[Cell(variable_key=u"Population02")]),#integer
                            Row(cells=[Cell(variable_key=u"Population03")])])]),#integer
            Section(title=u"Frågor om bemanning och personal",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Arsverke01")]),#numeric
                            Row(cells=[Cell(variable_key=u"Arsverke02")]),#numeric
                            Row(cells=[Cell(variable_key=u"Arsverke03")]),#numeric
                            Row(cells=[Cell(variable_key=u"Arsverke04")]),#numeric
                            Row(cells=[Cell(variable_key=u"Arsverke99",
                                            sum_of=["Arsverke01", "Arsverke02", "Arsverke03", "Arsverke04"])]),#numeric
                            Row(cells=[Cell(variable_key=u"Arsverke05", required=True)])]),#numeric
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Personer01")]),#integer
                            Row(cells=[Cell(variable_key=u"Personer02")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Personer99",
                                     sum_of=[u"Personer01", u"Personer02"])])]),#integer
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Personkomm")])])]),#comment
            Section(title=u"Frågor om ekonomi",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Utgift01")]),#integer
                            Row(cells=[Cell(variable_key=u"Utgift02")]),#integer
                            Row(cells=[Cell(variable_key=u"Utgift03")]),#integer
                            Row(cells=[Cell(variable_key=u"Utgift04")]),#integer
                            Row(cells=[Cell(variable_key=u"Utgift05")]),#integer
                            Row(cells=[Cell(variable_key=u"Utgift06")]),#integer
                            Row(cells=[Cell(variable_key=u"Utgift99",
                                            sum_of=[u"Utgift01", u"Utgift02", u"Utgift03",
                                                    u"Utgift04", u"Utgift05", u"Utgift06"])]),#integer
                            Row(cells=[Cell(variable_key=u"Utgift07")])]),#integer
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Intakt01")]),#integer
                            Row(cells=[Cell(variable_key=u"Intakt02")]),#integer
                            Row(cells=[Cell(variable_key=u"Intakt03")]),#integer
                            Row(cells=[Cell(variable_key=u"Intakt99",
                                            sum_of=[u"Intakt01", u"Intakt02", u"Intakt03"])])]),#integer
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Ekonomikomm")])])]),#comment
            Section(title=u"Bestånd – nyförvärv",
                    groups=[
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Bestand101", required=True),#integer
                                Cell(variable_key=u"Bestand201"),#integer
                                Cell(variable_key=u"Bestand301")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Bestand102"),#integer
                                Cell(variable_key=u"Bestand202"),#integer
                                Cell(variable_key=u"Bestand302")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Bestand103", required=True),#integer
                                Cell(variable_key=u"Bestand203"),#integer
                                Cell(variable_key=u"Bestand303")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Bestand104", required=True),#integer
                                Cell(variable_key=u"Bestand204"),#integer
                                Cell(variable_key=u"Bestand304")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Bestand105", required=True),#integer
                                Cell(variable_key=u"Bestand205"),#integer
                                Cell(variable_key=u"Bestand305")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Bestand106", required=True),#integer
                                Cell(variable_key=u"Bestand206"),#integer
                                Cell(variable_key=u"Bestand306")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Bestand107", required=True),#integer
                                Cell(variable_key=u"Bestand207"),#integer
                                Cell(variable_key=u"Bestand307")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Bestand108", required=True),#integer
                                Cell(variable_key=u"Bestand208"),#integer
                                Cell(variable_key=u"Bestand308")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Bestand109", required=True),#integer
                                Cell(variable_key=u"Bestand209")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Bestand110", required=True),#integer
                                Cell(variable_key=u"Bestand210"),#integer
                                Cell(variable_key=u"Bestand310")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Bestand111", required=True),#integer
                                Cell(variable_key=u"Bestand211"),#integer
                                Cell(variable_key=u"Bestand311")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Bestand112", required=True),#integer
                                Cell(variable_key=u"Bestand212"),#integer
                                Cell(variable_key=u"Bestand312")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Bestand113", required=True),#integer
                                Cell(variable_key=u"Bestand213"),#integer
                                Cell(variable_key=u"Bestand313")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Bestand199", #integer
                                     sum_of=['Bestand101', 'Bestand103',
                                             'Bestand104', 'Bestand105', 'Bestand106',
                                             'Bestand107', 'Bestand108', 'Bestand109',
                                             'Bestand110', 'Bestand111', 'Bestand112',
                                             'Bestand113']),
                                Cell(variable_key=u"Bestand299", #integer
                                     sum_of=['Bestand201', 'Bestand203',
                                             'Bestand204', 'Bestand205', 'Bestand206',
                                             'Bestand207', 'Bestand208', 'Bestand209',
                                             'Bestand210', 'Bestand211', 'Bestand212',
                                             'Bestand213']),
                                Cell(variable_key=u"Bestand399", #integer
                                     sum_of=['Bestand301', 'Bestand303',
                                             'Bestand304', 'Bestand305', 'Bestand306',
                                             'Bestand307', 'Bestand308', 'Bestand310',
                                             'Bestand311', 'Bestand312', 'Bestand313'])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Barn01", required=True)]),#integer
                            Row(cells=[Cell(variable_key=u"Barn02", required=True)]),#integer
                            Row(cells=[Cell(variable_key=u"Barn03", required=True)]),#integer
                            Row(cells=[Cell(variable_key=u"HCG04", required=True)]),#integer
                            Row(cells=[Cell(variable_key=u"Ref05", required=True)]),#integer
                            Row(cells=[Cell(variable_key=u"LasnedBest01", required=True)]),#integer
                            Row(cells=[Cell(variable_key=u"LasnedUtlan01", required=True)])]),#integer
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Titlar101"),#integer
                                Cell(variable_key=u"Titlar201"),#integer
                                Cell(variable_key=u"Titlar301"),#integer
                                Cell(variable_key=u"Titlar497", required=True,#integer
                                     sum_of=[u"Titlar101", u"Titlar201", u"Titlar301"])]),
                            Row(cells=[
                                Cell(variable_key=u"Titlar102"),#integer
                                Cell(variable_key=u"Titlar202"),#integer
                                Cell(variable_key=u"Titlar302"),#integer
                                Cell(variable_key=u"Titlar498", required=True,#integer
                                     sum_of=[u"Titlar102", u"Titlar202", u"Titlar302"])]),
                            Row(cells=[
                                Cell(variable_key=u"Titlar199",#integer
                                     sum_of=[u"Titlar101", u"Titlar102"]),
                                Cell(variable_key=u"Titlar299", #integer
                                     sum_of=[u"Titlar201", u"Titlar202"]),
                                Cell(variable_key=u"Titlar399", #integer
                                     sum_of=[u"Titlar301", u"Titlar302"]),
                                Cell(variable_key=u"Titlar499", #integer
                                     sum_of=[u"Titlar497", u"Titlar498"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Databas01")]),#integer
                            Row(cells=[Cell(variable_key=u"Databas02")]),#integer
                            Row(cells=[Cell(variable_key=u"Databas03")]),#integer
                            Row(cells=[Cell(variable_key=u"Databas04")]),#integer
                            Row(cells=[Cell(variable_key=u"Databas05")]),#integer
                            Row(cells=[Cell(variable_key=u"Databas06")]),#integer
                            Row(cells=[Cell(variable_key=u"Databas07")]),#integer
                            Row(cells=[Cell(variable_key=u"Databas08")]),#integer
                            Row(cells=[Cell(variable_key=u"Databas09")]),#integer
                            Row(cells=[Cell(variable_key=u"Databas99",#integer
                                            sum_of=[u"Databas01", u"Databas02", u"Databas03",
                                                    u"Databas04", u"Databas05", u"Databas06",
                                                    u"Databas07", u"Databas08", u"Databas09"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Databaskomm")])])]),#comment
            Section(title=u"Frågor om utlån, omlån och användning",
                    groups=[
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Inilan101"),#integer
                                Cell(variable_key=u"Omlan201"),#integer
                                Cell(variable_key=u"Utlan301",#integer
                                     sum_of=[u"Inilan101", u"Omlan201"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan102"),#integer
                                Cell(variable_key=u"Omlan202"),#integer
                                Cell(variable_key=u"Utlan302")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Inilan103"),#integer
                                Cell(variable_key=u"Omlan203"),#integer
                                Cell(variable_key=u"Utlan303",#integer
                                     sum_of=[u"Inilan103", u"Omlan203"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan104"),#integer
                                Cell(variable_key=u"Omlan204"),#integer
                                Cell(variable_key=u"Utlan304",#integer
                                     sum_of=[u"Inilan104", u"Omlan204"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan105"),#integer
                                Cell(variable_key=u"Omlan205"),#integer
                                Cell(variable_key=u"Utlan305",#integer
                                     sum_of=[u"Inilan105", u"Omlan205"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan106"),#integer
                                Cell(variable_key=u"Omlan206"),#integer
                                Cell(variable_key=u"Utlan306",#integer
                                     sum_of=[u"Inilan106", u"Omlan206"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan107"),#integer
                                Cell(variable_key=u"Omlan207"),#integer
                                Cell(variable_key=u"Utlan307",#integer
                                     sum_of=[u"Inilan107", u"Omlan207"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan108"),#integer
                                Cell(variable_key=u"Omlan208"),#integer
                                Cell(variable_key=u"Utlan308",#integer
                                     sum_of=[u"Inilan108", u"Omlan208"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan109"),#integer
                                Cell(variable_key=u"Omlan209"),#integer
                                Cell(variable_key=u"Utlan309",#integer
                                     sum_of=[u"Inilan109", u"Omlan209"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan110"),#integer
                                Cell(variable_key=u"Omlan210"),#integer
                                Cell(variable_key=u"Utlan310",#integer
                                     sum_of=[u"Inilan110", u"Omlan210"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan111"),#integer
                                Cell(variable_key=u"Omlan211"),#integer
                                Cell(variable_key=u"Utlan311",#integer
                                     sum_of=[u"Inilan111", u"Omlan211"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan112"),#integer
                                Cell(variable_key=u"Omlan212"),#integer
                                Cell(variable_key=u"Utlan312",#integer
                                     sum_of=[u"Inilan112", u"Omlan212"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan113"),#integer
                                Cell(variable_key=u"Omlan213"),#integer
                                Cell(variable_key=u"Utlan313",#integer
                                     sum_of=[u"Inilan113", u"Omlan213"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan199",#integer
                                     sum_of=[u"Inilan101", u"Inilan103", u"Inilan104",
                                            u"Inilan105", u"Inilan106", u"Inilan107",
                                            u"Inilan108", u"Inilan109", u"Inilan110",
                                           u"Inilan111", u"Inilan112", u"Inilan113"]),
                                Cell(variable_key=u"Omlan299",#integer
                                     sum_of=[u"Omlan201", u"Omlan203", u"Omlan204",
                                             u"Omlan205", u"Omlan206", u"Omlan207",
                                             u"Omlan208", u"Omlan209", u"Omlan210",
                                             u"Omlan211", u"Omlan212", u"Omlan213"]),
                                Cell(variable_key=u"Utlan399",#integer
                                     sum_of=[u"Utlan301", u"Utlan303", u"Utlan304",
                                             u"Utlan305", u"Utlan306", u"Utlan307",
                                             u"Utlan308", u"Utlan309", u"Utlan310",
                                             u"Utlan311", u"Utlan312", u"Utlan313"])])]),
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Laslan01")#integer
                            ]),
                            Row(cells=[
                                Cell(variable_key=u"Laslan02")#integer
                            ]),
                            Row(cells=[
                                Cell(variable_key=u"Laslan99")#integer
                            ])
                        ]),
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Fjarr101"),#integer
                                Cell(variable_key=u"Fjarr201"),#integer
                                Cell(variable_key=u"Fjarr397",#integer
                                     sum_of=[u"Fjarr101", u"Fjarr201"])]),
                            Row(cells=[
                                Cell(variable_key=u"Fjarr102"),#integer
                                Cell(variable_key=u"Fjarr202"),#integer
                                Cell(variable_key=u"Fjarr398",#integer
                                     sum_of=[u"Fjarr102", u"Fjarr202"])]),
                        ]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Utlankomm")])])]),#comment
            Section(title=u"Omsättningen av elektroniska medier, användning och lån",
                    groups=[
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Elan101"),#integer
                                Cell(variable_key=u"Elan201"),#integer
                                Cell(variable_key=u"Elan301")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Elan102"),#integer
                                Cell(variable_key=u"Elan202")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Elan103"),#integer
                                Cell(variable_key=u"Elan203")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Elan104"),#integer
                                Cell(variable_key=u"Elan204")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Elan105"),#integer
                                Cell(variable_key=u"Elan205")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Elan106"),#integer
                                Cell(variable_key=u"Elan206")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Elan107"),#integer
                                Cell(variable_key=u"Elan207")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Elan108"),#integer
                                Cell(variable_key=u"Elan208")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Elan109"),#integer
                                Cell(variable_key=u"Elan209")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Elan199",#integer
                                     sum_of=[u"Elan101", u"Elan102", u"Elan103",
                                             u"Elan104", u"Elan105", u"Elan106",
                                             u"Elan107", u"Elan108", u"Elan109"]),
                                Cell(variable_key=u"Elan299",#integer
                                     sum_of=[u"Elan201", u"Elan202", u"Elan203",
                                             u"Elan204", u"Elan205", u"Elan206",
                                             u"Elan207", u"Elan208", u"Elan209"]),
                                Cell(variable_key=u"Elan399",#integer
                                     sum_of=[u"Elan301"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Elankomm")])])]),#comment
            Section(title=u"Frågor om besök och aktiva låntagare",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Besok01", required=True)]),#integer
                            Row(cells=[Cell(variable_key=u"Besok02")]),#integer
                            Row(cells=[Cell(variable_key=u"Besok03")]),#integer
                            Row(cells=[Cell(variable_key=u"Besok04")]),#integer
                            Row(cells=[Cell(variable_key=u"Besok05")])]),#integer
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Aktiv01")]),#integer
                            Row(cells=[Cell(variable_key=u"Aktiv02")]),#integer
                            Row(cells=[Cell(variable_key=u"Aktiv04")]),#integer
                            Row(cells=[Cell(variable_key=u"Aktiv99",#integer
                                            sum_of=[u"Aktiv01", u"Aktiv02", u"Aktiv04"])]),
                            Row(cells=[Cell(variable_key=u"Aktiv03")])])]),#integer
            Section(title=u"Frågor om resurser och lokaler",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Resurs01", required=True)]),#integer
                            Row(cells=[Cell(variable_key=u"Resurs02")]),#integer
                            Row(cells=[Cell(variable_key=u"Resurs03")]),#integer
                            Row(cells=[Cell(variable_key=u"Resurs04")]),#integer
                            Row(cells=[Cell(variable_key=u"Resurs05")]),#integer
                            Row(cells=[Cell(variable_key=u"Resurs06")]),#integer
                            Row(cells=[Cell(variable_key=u"Resurs07", )]),#integer
                            Row(cells=[Cell(variable_key=u"Resurs08")]),#integer
                            Row(cells=[Cell(variable_key=u"Resurs09", )]),#integer
                            Row(cells=[Cell(variable_key=u"Resurs10")])]),#integer
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Besokkomm")])])]),#comment
            Section(title=u"Frågor om öppettider och nyttjande",
                    groups=[
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Open101"),#decimal
                                Cell(variable_key=u"Open201")]),#decimal
                            Row(cells=[
                                Cell(variable_key=u"Open102"),#decimal
                                Cell(variable_key=u"Open202")]),#decimal
                            Row(cells=[
                                Cell(variable_key=u"Open103"),#decimal
                                Cell(variable_key=u"Open203")]),#decimal
                            Row(cells=[
                                Cell(variable_key=u"Open104"),#decimal
                                Cell(variable_key=u"Open204")]),#decimal
                            Row(cells=[
                                Cell(variable_key=u"Open105"),#decimal
                                Cell(variable_key=u"Open205")]),#decimal
                            Row(cells=[
                                Cell(variable_key=u"Open106"),#decimal
                                Cell(variable_key=u"Open206")])]),#decimal
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Serv01")]),#integer
                            Row(cells=[Cell(variable_key=u"Serv02")]),#integer
                            Row(cells=[Cell(variable_key=u"Serv03")]),#integer
                            Row(cells=[Cell(variable_key=u"Serv04")]),#integer
                            Row(cells=[Cell(variable_key=u"Serv05")]),#integer
                            Row(cells=[Cell(variable_key=u"Serv06")]),#integer
                            Row(cells=[Cell(variable_key=u"Serv07")])]),#integer
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Openkomm")])])]),#comment
            Section(title=u"Aktiviteter",
                    groups=[
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Publ101", required=True),#integer
                                Cell(variable_key=u"Publ201")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ102", required=True),#integer
                                Cell(variable_key=u"Publ202")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ103", required=True),#integer
                                Cell(variable_key=u"Publ203")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ104", required=True),#integer
                                Cell(variable_key=u"Publ204")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ105", required=True),#integer
                                Cell(variable_key=u"Publ205")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ106", required=True),#integer
                                Cell(variable_key=u"Publ206")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ107", required=True),#integer
                                Cell(variable_key=u"Publ207")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ108", required=True),#integer
                                Cell(variable_key=u"Publ208")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ109", required=True),#integer
                                Cell(variable_key=u"Publ209")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ110", required=True),#integer
                                Cell(variable_key=u"Publ210")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ111", required=True),#integer
                                Cell(variable_key=u"Publ211")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ112", required=True),#integer
                                Cell(variable_key=u"Publ212")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ113", required=True),#integer
                                Cell(variable_key=u"Publ213")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ114", required=True),#integer
                                Cell(variable_key=u"Publ214")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ115", required=True),#integer
                                Cell(variable_key=u"Publ215")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ116", required=True),#integer
                                Cell(variable_key=u"Publ216")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ117", required=True),#integer
                                Cell(variable_key=u"Publ217")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ118", required=True),#integer
                                Cell(variable_key=u"Publ218")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ119", required=True),#integer
                                Cell(variable_key=u"Publ219")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ120", required=True),#integer
                                Cell(variable_key=u"Publ220")]),#integer
                            Row(cells=[
                                Cell(variable_key=u"Publ199",#integer
                                     sum_of=[u"Publ101", u"Publ102", u"Publ103",
                                             u"Publ104", u"Publ105", u"Publ106",
                                             u"Publ107", u"Publ108", u"Publ109",
                                             u"Publ110", u"Publ111", u"Publ112",
                                             u"Publ113", u"Publ114", u"Publ115",
                                             u"Publ116", u"Publ117", u"Publ118",
                                             u"Publ119", u"Publ120"]),
                                Cell(variable_key=u"Publ299",#integer
                                     sum_of=[u"Publ201", u"Publ202", u"Publ203",
                                             u"Publ204", u"Publ205", u"Publ206",
                                             u"Publ207", u"Publ208", u"Publ209",
                                             u"Publ210", u"Publ211", u"Publ212",
                                             u"Publ213", u"Publ214", u"Publ215",
                                             u"Publ216", u"Publ217", u"Publ218",
                                             u"Publ219", u"Publ220"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Publkomm")])])]),#comment
            Section(title=u"Slutligen",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"SCB01", required=True)]),#decimal
                            Row(cells=[Cell(variable_key=u"SCB02", required=True)])]),#decimal
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Alltkomm")])])])])#comment


def has_template(year):
    return year == 2014


def _default_template_from_survey(survey):
    rows = []
    if survey:
        for observation in survey.observations:
            variable = observation.variable
            rows.append(Row(cells=[Cell(variable_key=variable.key, types=["text"])])) #TODO: use variable.type??

    return SurveyTemplate(sections=[
        Section(title="",
                groups=[Group(rows=rows)])])


def survey_template(year, survey=None):
    year = int(year)
    if year >= 2014:
        return _survey_template_2014()

    return _default_template_from_survey(survey)

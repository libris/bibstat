# -*- coding: utf-8 -*-
from libstat.models import Section, Group, Cell, Row, SurveyTemplate


def _survey_template_2014():
    return SurveyTemplate(
        intro_text_variable_key="Introtext2014",
        sections=[
            Section(title=u"Frågor om biblioteksorganisationen",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Namn01", types=["text"])]),
                            Row(cells=[Cell(variable_key=u"Epost01", types=["email", "required"])]),
                            Row(cells=[Cell(variable_key=u"Tele01", types=["text"])]),
                            Row(cells=[Cell(variable_key=u"Plan01", types=["text"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"BemanService01", types=['required', 'integer'])]),
                            Row(cells=[Cell(variable_key=u"Integrerad01", types=['required', 'integer'])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Obeman01", types=['required', 'integer'])]),
                            Row(cells=[Cell(variable_key=u"ObemanLan01", types=['required', 'integer'])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Bokbuss01", types=['required', 'integer'])]),
                            Row(cells=[Cell(variable_key=u"BokbussHP01", types=['required', 'integer'])]),
                            Row(cells=[Cell(variable_key=u"Bokbil01", types=['integer'])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Population01", types=['integer'])]),
                            Row(cells=[Cell(variable_key=u"Population02", types=['integer'])]),
                            Row(cells=[Cell(variable_key=u"Population03", types=['integer'])])])]),
            Section(title=u"Frågor om bemanning och personal",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Arsverke01", types=['numeric'])]),
                            Row(cells=[Cell(variable_key=u"Arsverke02", types=['numeric'])]),
                            Row(cells=[Cell(variable_key=u"Arsverke03", types=['numeric'])]),
                            Row(cells=[Cell(variable_key=u"Arsverke04", types=['numeric'])]),
                            Row(cells=[Cell(variable_key=u"Arsverke99", types=['numeric'],
                                            sum_of=["Arsverke01", "Arsverke02", "Arsverke03", "Arsverke04"])]),
                            Row(cells=[Cell(variable_key=u"Arsverke05", types=['required', 'numeric'])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Personer01", types=['integer'])]),
                            Row(cells=[Cell(variable_key=u"Personer02", types=['integer'])]),
                            Row(cells=[
                                Cell(variable_key=u"Personer99", types=['integer'],
                                     sum_of=[u"Personer01", u"Personer02"])])]),
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Personkomm", types=["comment"])])])]),
            Section(title=u"Frågor om ekonomi",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Utgift01", types=['integer'])]),
                            Row(cells=[Cell(variable_key=u"Utgift02", types=['integer'])]),
                            Row(cells=[Cell(variable_key=u"Utgift03", types=['integer'])]),
                            Row(cells=[Cell(variable_key=u"Utgift04", types=['integer'])]),
                            Row(cells=[Cell(variable_key=u"Utgift05", types=['integer'])]),
                            Row(cells=[Cell(variable_key=u"Utgift06", types=['integer'])]),
                            Row(cells=[Cell(variable_key=u"Utgift99", types=['integer'],
                                            sum_of=[u"Utgift01", u"Utgift02", u"Utgift03",
                                                    u"Utgift04", u"Utgift05", u"Utgift06"])]),
                            Row(cells=[Cell(variable_key=u"Utgift07", types=['integer'])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Intakt01", types=['integer'])]),
                            Row(cells=[Cell(variable_key=u"Intakt02", types=['integer'])]),
                            Row(cells=[Cell(variable_key=u"Intakt03", types=['integer'])]),
                            Row(cells=[Cell(variable_key=u"Intakt99", types=['integer'],
                                            sum_of=[u"Intakt01", u"Intakt02", u"Intakt03"])])]),
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Ekonomikomm", types=["comment"])])])]),
            Section(title=u"Bestånd – nyförvärv",
                    groups=[
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Bestand101", types=['integer', 'required']),
                                Cell(variable_key=u"Bestand201", types=['integer']),
                                Cell(variable_key=u"Bestand301", types=['integer'])]),
                            Row(cells=[
                                Cell(variable_key=u"Bestand102", types=['integer']),
                                Cell(variable_key=u"Bestand202", types=['integer']),
                                Cell(variable_key=u"Bestand302", types=['integer'])]),
                            Row(cells=[
                                Cell(variable_key=u"Bestand103", types=['integer', 'required']),
                                Cell(variable_key=u"Bestand203", types=['integer']),
                                Cell(variable_key=u"Bestand303", types=['integer'])]),
                            Row(cells=[
                                Cell(variable_key=u"Bestand104", types=['integer', 'required']),
                                Cell(variable_key=u"Bestand204", types=['integer']),
                                Cell(variable_key=u"Bestand304", types=['integer'])]),
                            Row(cells=[
                                Cell(variable_key=u"Bestand105", types=['integer', 'required']),
                                Cell(variable_key=u"Bestand205", types=['integer']),
                                Cell(variable_key=u"Bestand305", types=['integer'])]),
                            Row(cells=[
                                Cell(variable_key=u"Bestand106", types=['integer', 'required']),
                                Cell(variable_key=u"Bestand206", types=['integer']),
                                Cell(variable_key=u"Bestand306", types=['integer'])]),
                            Row(cells=[
                                Cell(variable_key=u"Bestand107", types=['integer', 'required']),
                                Cell(variable_key=u"Bestand207", types=['integer']),
                                Cell(variable_key=u"Bestand307", types=['integer'])]),
                            Row(cells=[
                                Cell(variable_key=u"Bestand108", types=['integer', 'required']),
                                Cell(variable_key=u"Bestand208", types=['integer']),
                                Cell(variable_key=u"Bestand308", types=['integer'])]),
                            Row(cells=[
                                Cell(variable_key=u"Bestand109", types=['integer', 'required']),
                                Cell(variable_key=u"Bestand209", types=['integer'])]),
                            Row(cells=[
                                Cell(variable_key=u"Bestand110", types=['integer', 'required']),
                                Cell(variable_key=u"Bestand210", types=['integer']),
                                Cell(variable_key=u"Bestand310", types=['integer'])]),
                            Row(cells=[
                                Cell(variable_key=u"Bestand111", types=['integer', 'required']),
                                Cell(variable_key=u"Bestand211", types=['integer']),
                                Cell(variable_key=u"Bestand311", types=['integer'])]),
                            Row(cells=[
                                Cell(variable_key=u"Bestand112", types=['integer', 'required']),
                                Cell(variable_key=u"Bestand212", types=['integer']),
                                Cell(variable_key=u"Bestand312", types=['integer'])]),
                            Row(cells=[
                                Cell(variable_key=u"Bestand113", types=['integer', 'required']),
                                Cell(variable_key=u"Bestand213", types=['integer']),
                                Cell(variable_key=u"Bestand313", types=['integer'])]),
                            Row(cells=[
                                Cell(variable_key=u"Bestand199", types=['integer'],
                                     sum_of=['Bestand101', 'Bestand103',
                                             'Bestand104', 'Bestand105', 'Bestand106',
                                             'Bestand107', 'Bestand108', 'Bestand109',
                                             'Bestand110', 'Bestand111', 'Bestand112',
                                             'Bestand113']),
                                Cell(variable_key=u"Bestand299", types=['integer'],
                                     sum_of=['Bestand201', 'Bestand203',
                                             'Bestand204', 'Bestand205', 'Bestand206',
                                             'Bestand207', 'Bestand208', 'Bestand209',
                                             'Bestand210', 'Bestand211', 'Bestand212',
                                             'Bestand213']),
                                Cell(variable_key=u"Bestand399", types=['integer'],
                                     sum_of=['Bestand301', 'Bestand303',
                                             'Bestand304', 'Bestand305', 'Bestand306',
                                             'Bestand307', 'Bestand308', 'Bestand310',
                                             'Bestand311', 'Bestand312', 'Bestand313'])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Barn01", types=['required', 'integer'])]),
                            Row(cells=[Cell(variable_key=u"Barn02", types=['required', 'integer'])]),
                            Row(cells=[Cell(variable_key=u"Barn03", types=['required', 'integer'])]),
                            Row(cells=[Cell(variable_key=u"HCG04", types=['required', 'integer'])]),
                            Row(cells=[Cell(variable_key=u"Ref05", types=['required', 'integer'])]),
                            Row(cells=[Cell(variable_key=u"LasnedBest01", types=['required', 'integer'])]),
                            Row(cells=[Cell(variable_key=u"LasnedUtlan01", types=['required', 'integer'])])]),
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Titlar101", types=["integer"]),
                                Cell(variable_key=u"Titlar201", types=["integer"]),
                                Cell(variable_key=u"Titlar301", types=["integer"]),
                                Cell(variable_key=u"Titlar497", types=["integer", "required"])]),
                            Row(cells=[
                                Cell(variable_key=u"Titlar102", types=["integer"]),
                                Cell(variable_key=u"Titlar202", types=["integer"]),
                                Cell(variable_key=u"Titlar302", types=["integer"]),
                                Cell(variable_key=u"Titlar498", types=["integer", "required"])]),
                            Row(cells=[
                                Cell(variable_key=u"Titlar199", types=["integer"],
                                     sum_of=[u"Titlar101", u"Titlar102"]),
                                Cell(variable_key=u"Titlar299", types=["integer"],
                                     sum_of=[u"Titlar201", u"Titlar202"]),
                                Cell(variable_key=u"Titlar399", types=["integer"],
                                     sum_of=[u"Titlar301", u"Titlar302"]),
                                Cell(variable_key=u"Titlar499", types=["integer"],
                                     sum_of=[u"Titlar497", u"Titlar498"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Databas01", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Databas02", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Databas03", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Databas04", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Databas05", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Databas06", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Databas07", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Databas08", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Databas09", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Databas99", types=["integer"],
                                            sum_of=[u"Databas01", u"Databas02", u"Databas03",
                                                    u"Databas04", u"Databas05", u"Databas06",
                                                    u"Databas07", u"Databas08", u"Databas09"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Databaskomm", types=["comment"])])])]),
            Section(title=u"Frågor om utlån, omlån och användning",
                    groups=[
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Inilan101", types=["integer"]),
                                Cell(variable_key=u"Omlan201", types=["integer"]),
                                Cell(variable_key=u"Utlan301", types=["integer"],
                                     sum_of=[u"Inilan101", u"Omlan201"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan102", types=["integer"]),
                                Cell(variable_key=u"Omlan202", types=["integer"]),
                                Cell(variable_key=u"Utlan302", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan103", types=["integer"]),
                                Cell(variable_key=u"Omlan203", types=["integer"]),
                                Cell(variable_key=u"Utlan303", types=["integer"],
                                     sum_of=[u"Inilan103", u"Omlan203"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan104", types=["integer"]),
                                Cell(variable_key=u"Omlan204", types=["integer"]),
                                Cell(variable_key=u"Utlan304", types=["integer"],
                                     sum_of=[u"Inilan104", u"Omlan204"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan105", types=["integer"]),
                                Cell(variable_key=u"Omlan205", types=["integer"]),
                                Cell(variable_key=u"Utlan305", types=["integer"],
                                     sum_of=[u"Inilan105", u"Omlan205"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan106", types=["integer"]),
                                Cell(variable_key=u"Omlan206", types=["integer"]),
                                Cell(variable_key=u"Utlan306", types=["integer"],
                                     sum_of=[u"Inilan106", u"Omlan206"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan107", types=["integer"]),
                                Cell(variable_key=u"Omlan207", types=["integer"]),
                                Cell(variable_key=u"Utlan307", types=["integer"],
                                     sum_of=[u"Inilan107", u"Omlan207"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan108", types=["integer"]),
                                Cell(variable_key=u"Omlan208", types=["integer"]),
                                Cell(variable_key=u"Utlan308", types=["integer"],
                                     sum_of=[u"Inilan108", u"Omlan208"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan109", types=["integer"]),
                                Cell(variable_key=u"Omlan209", types=["integer"]),
                                Cell(variable_key=u"Utlan309", types=["integer"],
                                     sum_of=[u"Inilan109", u"Omlan209"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan110", types=["integer"]),
                                Cell(variable_key=u"Omlan210", types=["integer"]),
                                Cell(variable_key=u"Utlan310", types=["integer"],
                                     sum_of=[u"Inilan110", u"Omlan210"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan111", types=["integer"]),
                                Cell(variable_key=u"Omlan211", types=["integer"]),
                                Cell(variable_key=u"Utlan311", types=["integer"],
                                     sum_of=[u"Inilan111", u"Omlan211"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan112", types=["integer"]),
                                Cell(variable_key=u"Omlan212", types=["integer"]),
                                Cell(variable_key=u"Utlan312", types=["integer"],
                                     sum_of=[u"Inilan112", u"Omlan212"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan113", types=["integer"]),
                                Cell(variable_key=u"Omlan213", types=["integer"]),
                                Cell(variable_key=u"Utlan313", types=["integer"],
                                     sum_of=[u"Inilan113", u"Omlan213"])]),
                            Row(cells=[
                                Cell(variable_key=u"Inilan199", types=["integer"]),
                                Cell(variable_key=u"Omlan299", types=["integer"]),
                                Cell(variable_key=u"Utlan399", types=["integer"],
                                     sum_of=[u"Inilan199", u"Omlan299"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Laslan01", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Laslan02", types=["integer"])])]),
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Fjarr101", types=["integer"]),
                                Cell(variable_key=u"Fjarr201", types=["integer"]),
                                Cell(variable_key=u"Fjarr397", types=["integer"],
                                     sum_of=[u"Fjarr101", u"Fjarr201"])]),
                            Row(cells=[
                                Cell(variable_key=u"Fjarr102", types=["integer"]),
                                Cell(variable_key=u"Fjarr202", types=["integer"]),
                                Cell(variable_key=u"Fjarr398", types=["integer"],
                                     sum_of=[u"Fjarr102", u"Fjarr202"])]),
                        ]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Utlankomm", types=["comment"])])])]),
            Section(title=u"Omsättningen av elektroniska medier, användning och lån",
                    groups=[
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Elan101", types=["integer"]),
                                Cell(variable_key=u"Elan201", types=["integer"]),
                                Cell(variable_key=u"Elan301", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Elan102", types=["integer"]),
                                Cell(variable_key=u"Elan202", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Elan103", types=["integer"]),
                                Cell(variable_key=u"Elan203", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Elan104", types=["integer"]),
                                Cell(variable_key=u"Elan204", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Elan105", types=["integer"]),
                                Cell(variable_key=u"Elan205", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Elan106", types=["integer"]),
                                Cell(variable_key=u"Elan206", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Elan107", types=["integer"]),
                                Cell(variable_key=u"Elan207", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Elan108", types=["integer"]),
                                Cell(variable_key=u"Elan208", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Elan109", types=["integer"]),
                                Cell(variable_key=u"Elan209", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Elan199", types=["integer"],
                                     sum_of=[u"Elan101", u"Elan102", u"Elan103",
                                             u"Elan104", u"Elan105", u"Elan106",
                                             u"Elan107", u"Elan108", u"Elan109"]),
                                Cell(variable_key=u"Elan299", types=["integer"],
                                     sum_of=[u"Elan201", u"Elan202", u"Elan203",
                                             u"Elan204", u"Elan205", u"Elan206",
                                             u"Elan207", u"Elan208", u"Elan209"]),
                                Cell(variable_key=u"Elan399", types=["integer"],
                                     sum_of=[u"Elan301"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Elankomm", types=["comment"])])])]),
            Section(title=u"Frågor om besök och aktiva låntagare",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Besok01", types=["integer", "required"])]),
                            Row(cells=[Cell(variable_key=u"Besok02", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Besok03", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Besok04", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Besok05", types=["integer"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Aktiv01", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Aktiv02", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Aktiv04", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Aktiv99", types=["integer"],
                                            sum_of=[u"Aktiv01", u"Aktiv02", u"Aktiv04"])]),
                            Row(cells=[Cell(variable_key=u"Aktiv03", types=["integer"])])])]),
            Section(title=u"Frågor om resurser och lokaler",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Resurs01", types=["integer", "required"])]),
                            Row(cells=[Cell(variable_key=u"Resurs02", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Resurs03", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Resurs04", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Resurs05", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Resurs06", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Resurs07", types=["integer", "required"])]),
                            Row(cells=[Cell(variable_key=u"Resurs08", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Resurs09", types=["integer", "required"])]),
                            Row(cells=[Cell(variable_key=u"Resurs10", types=["integer"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Besokkomm", types=["comment"])])])]),
            Section(title=u"Frågor om öppettider och nyttjande",
                    groups=[
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Open101", types=["integer"]),
                                Cell(variable_key=u"Open201", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Open102", types=["integer"]),
                                Cell(variable_key=u"Open202", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Open103", types=["integer"]),
                                Cell(variable_key=u"Open203", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Open104", types=["integer"]),
                                Cell(variable_key=u"Open204", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Open105", types=["integer"]),
                                Cell(variable_key=u"Open205", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Open106", types=["integer"]),
                                Cell(variable_key=u"Open206", types=["integer"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Serv01", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Serv02", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Serv03", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Serv04", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Serv05", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Serv06", types=["integer"])]),
                            Row(cells=[Cell(variable_key=u"Serv07", types=["integer"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Openkomm", types=["comment"])])])]),
            Section(title=u"Publika aktiviter",
                    groups=[
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key=u"Publ101", types=["integer", "required"]),
                                Cell(variable_key=u"Publ201", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ102", types=["integer", "required"]),
                                Cell(variable_key=u"Publ202", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ103", types=["integer", "required"]),
                                Cell(variable_key=u"Publ203", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ104", types=["integer", "required"]),
                                Cell(variable_key=u"Publ204", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ105", types=["integer", "required"]),
                                Cell(variable_key=u"Publ205", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ106", types=["integer", "required"]),
                                Cell(variable_key=u"Publ206", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ107", types=["integer", "required"]),
                                Cell(variable_key=u"Publ207", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ108", types=["integer", "required"]),
                                Cell(variable_key=u"Publ208", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ109", types=["integer", "required"]),
                                Cell(variable_key=u"Publ209", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ110", types=["integer", "required"]),
                                Cell(variable_key=u"Publ210", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ111", types=["integer", "required"]),
                                Cell(variable_key=u"Publ211", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ112", types=["integer", "required"]),
                                Cell(variable_key=u"Publ212", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ113", types=["integer", "required"]),
                                Cell(variable_key=u"Publ213", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ114", types=["integer", "required"]),
                                Cell(variable_key=u"Publ214", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ115", types=["integer", "required"]),
                                Cell(variable_key=u"Publ215", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ116", types=["integer", "required"]),
                                Cell(variable_key=u"Publ216", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ117", types=["integer", "required"]),
                                Cell(variable_key=u"Publ217", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ118", types=["integer", "required"]),
                                Cell(variable_key=u"Publ218", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ119", types=["integer", "required"]),
                                Cell(variable_key=u"Publ219", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ120", types=["integer", "required"]),
                                Cell(variable_key=u"Publ220", types=["integer"])]),
                            Row(cells=[
                                Cell(variable_key=u"Publ199", types=["integer"],
                                     sum_of=[u"Publ101", u"Publ102", u"Publ103",
                                             u"Publ104", u"Publ105", u"Publ106",
                                             u"Publ107", u"Publ108", u"Publ109",
                                             u"Publ110", u"Publ111", u"Publ112",
                                             u"Publ113", u"Publ114", u"Publ115",
                                             u"Publ116", u"Publ117", u"Publ118",
                                             u"Publ119", u"Publ120"]),
                                Cell(variable_key=u"Publ299", types=["integer"],
                                     sum_of=[u"Publ201", u"Publ202", u"Publ203",
                                             u"Publ204", u"Publ205", u"Publ206",
                                             u"Publ207", u"Publ208", u"Publ209",
                                             u"Publ210", u"Publ211", u"Publ212",
                                             u"Publ213", u"Publ214", u"Publ215",
                                             u"Publ216", u"Publ217", u"Publ218",
                                             u"Publ219", u"Publ220"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Publkomm", types=["comment"])])])]),
            Section(title=u"Slutligen",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"SCB01", types=["decimal", "required"])]),
                            Row(cells=[Cell(variable_key=u"SCB02", types=["decimal", "required"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key=u"Alltkomm", types=["comment"])])])])])


def has_template(year):
    return year == 2014


def _default_template_from_survey(survey):
    rows = []
    if survey:
        for observation in survey.observations:
            variable = observation.variable
            rows.append(Row(cells=[Cell(variable_key=variable.key, types=["text"])]))

    return SurveyTemplate(sections=[
        Section(title="",
                groups=[Group(rows=rows)])])


def survey_template(year, survey=None):
    year = int(year)
    if year >= 2014:
        return _survey_template_2014()

    return _default_template_from_survey(survey)

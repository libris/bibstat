from libstat.models import Section, Group, Cell, Row, SurveyTemplate


def _survey_template_base():
    return SurveyTemplate(
        intro_text_variable_key="Introtext2014",
        sections=[
            Section(title="Frågor om biblioteksorganisationen",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Namn01")]),
                            Row(cells=[Cell(variable_key="Epost01", required=True)]),
                            Row(cells=[Cell(variable_key="Tele01")]),
                            Row(cells=[Cell(variable_key="Plan01")])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="BemanService01", required=True)]),
                            Row(cells=[Cell(variable_key="Integrerad01", required=True)])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Obeman01", required=True)]),
                            Row(cells=[Cell(variable_key="ObemanLan01", required=True)])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Bokbuss01", required=True)]),
                            Row(cells=[Cell(variable_key="BokbussHP01", required=True)]),
                            Row(cells=[Cell(variable_key="Bokbil01")])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Population01")]),
                            Row(cells=[Cell(variable_key="Population02")]),
                            Row(cells=[Cell(variable_key="Population03")])])]),
            Section(title="Frågor om bemanning och personal",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Arsverke01")]),
                            Row(cells=[Cell(variable_key="Arsverke02")]),
                            Row(cells=[Cell(variable_key="Arsverke03")]),
                            Row(cells=[Cell(variable_key="Arsverke04")]),
                            Row(cells=[Cell(variable_key="Arsverke99",
                                            sum_of=["Arsverke01", "Arsverke02", "Arsverke03", "Arsverke04"])]),
                            Row(cells=[Cell(variable_key="Arsverke05", required=True)])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Personer01")]),
                            Row(cells=[Cell(variable_key="Personer02")]),
                            Row(cells=[
                                Cell(variable_key="Personer99",
                                     sum_of=["Personer01", "Personer02"])])]),
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key="Personkomm")])])]),
            Section(title="Frågor om ekonomi",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Utgift01")]),
                            Row(cells=[Cell(variable_key="Utgift02")]),
                            Row(cells=[Cell(variable_key="Utgift03")]),
                            Row(cells=[Cell(variable_key="Utgift04")]),
                            Row(cells=[Cell(variable_key="Utgift05")]),
                            Row(cells=[Cell(variable_key="Utgift06")]),
                            Row(cells=[Cell(variable_key="Utgift99",
                                            sum_of=["Utgift01", "Utgift02", "Utgift03",
                                                    "Utgift04", "Utgift05", "Utgift06"])]),
                            Row(cells=[Cell(variable_key="Utgift07")])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Intakt01")]),
                            Row(cells=[Cell(variable_key="Intakt02")]),
                            Row(cells=[Cell(variable_key="Intakt03")]),
                            Row(cells=[Cell(variable_key="Intakt99",
                                            sum_of=["Intakt01", "Intakt02", "Intakt03"])])]),
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key="Ekonomikomm")])])]),
            Section(title="Bestånd – nyförvärv",
                    groups=[
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key="Bestand101", required=True, has_part=["Bestand201", "Bestand102"]),
                                Cell(variable_key="Bestand201", has_part="Bestand202", part_of="Bestand101"),
                                Cell(variable_key="Bestand301", has_part="Bestand302")]),
                            Row(cells=[
                                Cell(variable_key="Bestand102", has_part="Bestand202", part_of="Bestand101"),
                                Cell(variable_key="Bestand202", part_of=["Bestand201", "Bestand102"]),
                                Cell(variable_key="Bestand302", part_of="Bestand301")]),
                            Row(cells=[
                                Cell(variable_key="Bestand103", has_part="Bestand203", required=True),
                                Cell(variable_key="Bestand203", part_of="Bestand103"),
                                Cell(variable_key="Bestand303")]),
                            Row(cells=[
                                Cell(variable_key="Bestand104", has_part="Bestand204", required=True),
                                Cell(variable_key="Bestand204", part_of="Bestand104"),
                                Cell(variable_key="Bestand304")]),
                            Row(cells=[
                                Cell(variable_key="Bestand105", has_part="Bestand205", required=True),
                                Cell(variable_key="Bestand205", part_of="Bestand105"),
                                Cell(variable_key="Bestand305")]),
                            Row(cells=[
                                Cell(variable_key="Bestand106", has_part="Bestand206", required=True),
                                Cell(variable_key="Bestand206", part_of="Bestand106"),
                                Cell(variable_key="Bestand306")]),
                            Row(cells=[
                                Cell(variable_key="Bestand107", has_part="Bestand207", required=True),
                                Cell(variable_key="Bestand207", part_of="Bestand107"),
                                Cell(variable_key="Bestand307")]),
                            Row(cells=[
                                Cell(variable_key="Bestand108", has_part="Bestand208", required=True),
                                Cell(variable_key="Bestand208", part_of="Bestand108"),
                                Cell(variable_key="Bestand308")]),
                            Row(cells=[
                                Cell(variable_key="Bestand109", has_part="Bestand209", required=True),
                                Cell(variable_key="Bestand209", part_of="Bestand109")]),
                            Row(cells=[
                                Cell(variable_key="Bestand110", has_part="Bestand210", required=True),
                                Cell(variable_key="Bestand210", part_of="Bestand110"),
                                Cell(variable_key="Bestand310")]),
                            Row(cells=[
                                Cell(variable_key="Bestand111", has_part="Bestand211", required=True),
                                Cell(variable_key="Bestand211", part_of="Bestand111"),
                                Cell(variable_key="Bestand311")]),
                            Row(cells=[
                                Cell(variable_key="Bestand112", has_part="Bestand212", required=True),
                                Cell(variable_key="Bestand212", part_of="Bestand112"),
                                Cell(variable_key="Bestand312")]),
                            Row(cells=[
                                Cell(variable_key="Bestand113", has_part="Bestand213", required=True),
                                Cell(variable_key="Bestand213", part_of="Bestand113"),
                                Cell(variable_key="Bestand313")]),
                            Row(cells=[
                                Cell(variable_key="Bestand199",
                                     has_part="Bestand299",
                                     sum_of=['Bestand101', 'Bestand103',
                                             'Bestand104', 'Bestand105', 'Bestand106',
                                             'Bestand107', 'Bestand108', 'Bestand109',
                                             'Bestand110', 'Bestand111', 'Bestand112',
                                             'Bestand113']), 
                                Cell(variable_key="Bestand299",
                                     part_of="Bestand199",
                                     sum_of=['Bestand201', 'Bestand203',
                                             'Bestand204', 'Bestand205', 'Bestand206',
                                             'Bestand207', 'Bestand208', 'Bestand209',
                                             'Bestand210', 'Bestand211', 'Bestand212',
                                             'Bestand213']), 
                                Cell(variable_key="Bestand399",
                                     sum_of=['Bestand301', 'Bestand303',
                                             'Bestand304', 'Bestand305', 'Bestand306',
                                             'Bestand307', 'Bestand308', 'Bestand310',
                                             'Bestand311', 'Bestand312', 'Bestand313'])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Barn01", required=True)]),
                            Row(cells=[Cell(variable_key="Barn02", required=True)]),
                            Row(cells=[Cell(variable_key="Barn03", required=True)]),
                            Row(cells=[Cell(variable_key="HCG04", required=True)]),
                            Row(cells=[Cell(variable_key="Ref05", required=True)]),
                            Row(cells=[Cell(variable_key="LasnedBest01", required=True)]),
                            Row(cells=[Cell(variable_key="LasnedUtlan01", required=True)])]),
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key="Titlar101"),
                                Cell(variable_key="Titlar201"),
                                Cell(variable_key="Titlar301"),
                                Cell(variable_key="Titlar497", required=True,
                                     sum_of=["Titlar101", "Titlar201", "Titlar301"])]),
                            Row(cells=[
                                Cell(variable_key="Titlar102"),
                                Cell(variable_key="Titlar202"),
                                Cell(variable_key="Titlar302"),
                                Cell(variable_key="Titlar498", required=True,
                                     sum_of=["Titlar102", "Titlar202", "Titlar302"])]),
                            Row(cells=[
                                Cell(variable_key="Titlar199",
                                     sum_of=["Titlar101", "Titlar102"]),
                                Cell(variable_key="Titlar299", 
                                     sum_of=["Titlar201", "Titlar202"]),
                                Cell(variable_key="Titlar399", 
                                     sum_of=["Titlar301", "Titlar302"]),
                                Cell(variable_key="Titlar499", 
                                     sum_of=["Titlar497", "Titlar498"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Databas01")]),
                            Row(cells=[Cell(variable_key="Databas02")]),
                            Row(cells=[Cell(variable_key="Databas03")]),
                            Row(cells=[Cell(variable_key="Databas04")]),
                            Row(cells=[Cell(variable_key="Databas05")]),
                            Row(cells=[Cell(variable_key="Databas06")]),
                            Row(cells=[Cell(variable_key="Databas07")]),
                            Row(cells=[Cell(variable_key="Databas08")]),
                            Row(cells=[Cell(variable_key="Databas09")]),
                            Row(cells=[Cell(variable_key="Databas99",
                                            sum_of=["Databas01", "Databas02", "Databas03",
                                                    "Databas04", "Databas05", "Databas06",
                                                    "Databas07", "Databas08", "Databas09"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Databaskomm")])])]),
            Section(title="Frågor om utlån, omlån och användning",
                    groups=[
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key="Inilan101", has_part="Inilan102"),
                                Cell(variable_key="Omlan201", has_part="Omlan202"),
                                Cell(variable_key="Utlan301", has_part="Utlan302",
                                     sum_of=["Inilan101", "Omlan201"])]),
                            Row(cells=[
                                Cell(variable_key="Inilan102", part_of="Inilan101"),
                                Cell(variable_key="Omlan202", part_of="Omlan201"),
                                Cell(variable_key="Utlan302", part_of="Utlan301",
                                     sum_of=["Inilan102", "Omlan202"])]),
                            Row(cells=[
                                Cell(variable_key="Inilan103"),
                                Cell(variable_key="Omlan203"),
                                Cell(variable_key="Utlan303",
                                     sum_of=["Inilan103", "Omlan203"])]),
                            Row(cells=[
                                Cell(variable_key="Inilan104"),
                                Cell(variable_key="Omlan204"),
                                Cell(variable_key="Utlan304",
                                     sum_of=["Inilan104", "Omlan204"])]),
                            Row(cells=[
                                Cell(variable_key="Inilan105"),
                                Cell(variable_key="Omlan205"),
                                Cell(variable_key="Utlan305",
                                     sum_of=["Inilan105", "Omlan205"])]),
                            Row(cells=[
                                Cell(variable_key="Inilan106"),
                                Cell(variable_key="Omlan206"),
                                Cell(variable_key="Utlan306",
                                     sum_of=["Inilan106", "Omlan206"])]),
                            Row(cells=[
                                Cell(variable_key="Inilan107"),
                                Cell(variable_key="Omlan207"),
                                Cell(variable_key="Utlan307",
                                     sum_of=["Inilan107", "Omlan207"])]),
                            Row(cells=[
                                Cell(variable_key="Inilan108"),
                                Cell(variable_key="Omlan208"),
                                Cell(variable_key="Utlan308",
                                     sum_of=["Inilan108", "Omlan208"])]),
                            Row(cells=[
                                Cell(variable_key="Inilan109"),
                                Cell(variable_key="Omlan209"),
                                Cell(variable_key="Utlan309",
                                     sum_of=["Inilan109", "Omlan209"])]),
                            Row(cells=[
                                Cell(variable_key="Inilan110"),
                                Cell(variable_key="Omlan210"),
                                Cell(variable_key="Utlan310",
                                     sum_of=["Inilan110", "Omlan210"])]),
                            Row(cells=[
                                Cell(variable_key="Inilan111"),
                                Cell(variable_key="Omlan211"),
                                Cell(variable_key="Utlan311",
                                     sum_of=["Inilan111", "Omlan211"])]),
                            Row(cells=[
                                Cell(variable_key="Inilan112"),
                                Cell(variable_key="Omlan212"),
                                Cell(variable_key="Utlan312",
                                     sum_of=["Inilan112", "Omlan212"])]),
                            Row(cells=[
                                Cell(variable_key="Inilan113"),
                                Cell(variable_key="Omlan213"),
                                Cell(variable_key="Utlan313",
                                     sum_of=["Inilan113", "Omlan213"])]),
                            Row(cells=[
                                Cell(variable_key="Inilan199",
                                     sum_of=["Inilan101", "Inilan103", "Inilan104",
                                            "Inilan105", "Inilan106", "Inilan107",
                                            "Inilan108", "Inilan109", "Inilan110",
                                           "Inilan111", "Inilan112", "Inilan113"]),
                                Cell(variable_key="Omlan299",
                                     sum_of=["Omlan201", "Omlan203", "Omlan204",
                                             "Omlan205", "Omlan206", "Omlan207",
                                             "Omlan208", "Omlan209", "Omlan210",
                                             "Omlan211", "Omlan212", "Omlan213"]),
                                Cell(variable_key="Utlan399",
                                     sum_of=["Utlan301", "Utlan303", "Utlan304",
                                             "Utlan305", "Utlan306", "Utlan307",
                                             "Utlan308", "Utlan309", "Utlan310",
                                             "Utlan311", "Utlan312", "Utlan313"])])]),
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key="Laslan01")
                            ]),
                            Row(cells=[
                                Cell(variable_key="Laslan02")
                            ]),
                            Row(cells=[
                                Cell(variable_key="Laslan99")
                            ])
                        ]),
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key="Fjarr101"),
                                Cell(variable_key="Fjarr201"),
                                Cell(variable_key="Fjarr397",
                                     sum_of=["Fjarr101", "Fjarr201"])]),
                            Row(cells=[
                                Cell(variable_key="Fjarr102"),
                                Cell(variable_key="Fjarr202"),
                                Cell(variable_key="Fjarr398",
                                     sum_of=["Fjarr102", "Fjarr202"])]),
                        ]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Utlankomm")])])]),
            Section(title="Omsättningen av elektroniska medier, användning och lån",
                    groups=[
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key="Elan101"),
                                Cell(variable_key="Elan201"),
                                Cell(variable_key="Elan301")]),
                            Row(cells=[
                                Cell(variable_key="Elan102"),
                                Cell(variable_key="Elan202")]),
                            Row(cells=[
                                Cell(variable_key="Elan103"),
                                Cell(variable_key="Elan203")]),
                            Row(cells=[
                                Cell(variable_key="Elan104"),
                                Cell(variable_key="Elan204")]),
                            Row(cells=[
                                Cell(variable_key="Elan105"),
                                Cell(variable_key="Elan205")]),
                            Row(cells=[
                                Cell(variable_key="Elan106"),
                                Cell(variable_key="Elan206")]),
                            Row(cells=[
                                Cell(variable_key="Elan107"),
                                Cell(variable_key="Elan207")]),
                            Row(cells=[
                                Cell(variable_key="Elan108"),
                                Cell(variable_key="Elan208")]),
                            Row(cells=[
                                Cell(variable_key="Elan109"),
                                Cell(variable_key="Elan209")]),
                            Row(cells=[
                                Cell(variable_key="Elan199",
                                     sum_of=["Elan101", "Elan102", "Elan103",
                                             "Elan104", "Elan105", "Elan106",
                                             "Elan107", "Elan108", "Elan109"]),
                                Cell(variable_key="Elan299",
                                     sum_of=["Elan201", "Elan202", "Elan203",
                                             "Elan204", "Elan205", "Elan206",
                                             "Elan207", "Elan208", "Elan209"]),
                                Cell(variable_key="Elan399",
                                     sum_of=["Elan301"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Elankomm")])])]),
            Section(title="Frågor om besök och aktiva låntagare",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Besok01", required=True)]),
                            Row(cells=[Cell(variable_key="Besok02")]),
                            Row(cells=[Cell(variable_key="Besok03")]),
                            Row(cells=[Cell(variable_key="Besok04")]),
                            Row(cells=[Cell(variable_key="Besok05")])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Aktiv01")]),
                            Row(cells=[Cell(variable_key="Aktiv02")]),
                            Row(cells=[Cell(variable_key="Aktiv04")]),
                            Row(cells=[Cell(variable_key="Aktiv99",
                                            sum_of=["Aktiv01", "Aktiv02", "Aktiv04"])]),
                            Row(cells=[Cell(variable_key="Aktiv03")])])]),
            Section(title="Frågor om resurser och lokaler",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Resurs01", required=True)]),
                            Row(cells=[Cell(variable_key="Resurs02")]),
                            Row(cells=[Cell(variable_key="Resurs03")]),
                            Row(cells=[Cell(variable_key="Resurs04")]),
                            Row(cells=[Cell(variable_key="Resurs05")]),
                            Row(cells=[Cell(variable_key="Resurs06")]),
                            Row(cells=[Cell(variable_key="Resurs07", required=True)]),
                            Row(cells=[Cell(variable_key="Resurs08")]),
                            Row(cells=[Cell(variable_key="Resurs09", required=True)]),
                            Row(cells=[Cell(variable_key="Resurs10")])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Besokkomm")])])]),
            Section(title="Frågor om öppettider och nyttjande",
                    groups=[
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key="Open101"),
                                Cell(variable_key="Open201")]),
                            Row(cells=[
                                Cell(variable_key="Open102"),
                                Cell(variable_key="Open202")]),
                            Row(cells=[
                                Cell(variable_key="Open103"),
                                Cell(variable_key="Open203")]),
                            Row(cells=[
                                Cell(variable_key="Open104"),
                                Cell(variable_key="Open204")]),
                            Row(cells=[
                                Cell(variable_key="Open105"),
                                Cell(variable_key="Open205")]),
                            Row(cells=[
                                Cell(variable_key="Open106"),
                                Cell(variable_key="Open206")])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Serv01")]),
                            Row(cells=[Cell(variable_key="Serv02")]),
                            Row(cells=[Cell(variable_key="Serv03")]),
                            Row(cells=[Cell(variable_key="Serv04")]),
                            Row(cells=[Cell(variable_key="Serv05")]),
                            Row(cells=[Cell(variable_key="Serv06")]),
                            Row(cells=[Cell(variable_key="Serv07")])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Openkomm")])])]),
            Section(title="Aktiviteter",
                    groups=[
                        Group(rows=[
                            Row(cells=[
                                Cell(variable_key="Publ101", required=True, has_part="Publ201"),
                                Cell(variable_key="Publ201", part_of="Publ101")]),
                            Row(cells=[
                                Cell(variable_key="Publ102", required=True, has_part="Publ202"),
                                Cell(variable_key="Publ202", part_of="Publ102")]),
                            Row(cells=[
                                Cell(variable_key="Publ103", required=True, has_part="Publ203"),
                                Cell(variable_key="Publ203", part_of="Publ103")]),
                            Row(cells=[
                                Cell(variable_key="Publ104", required=True, has_part="Publ204"),
                                Cell(variable_key="Publ204", part_of="Publ104")]),
                            Row(cells=[
                                Cell(variable_key="Publ105", required=True, has_part="Publ205"),
                                Cell(variable_key="Publ205", part_of="Publ105")]),
                            Row(cells=[
                                Cell(variable_key="Publ106", required=True, has_part="Publ206"),
                                Cell(variable_key="Publ206", part_of="Publ106")]),
                            Row(cells=[
                                Cell(variable_key="Publ107", required=True, has_part="Publ207"),
                                Cell(variable_key="Publ207", part_of="Publ107")]),
                            Row(cells=[
                                Cell(variable_key="Publ108", required=True, has_part="Publ208"),
                                Cell(variable_key="Publ208", part_of="Publ108")]),
                            Row(cells=[
                                Cell(variable_key="Publ109", required=True, has_part="Publ209"),
                                Cell(variable_key="Publ209", part_of="Publ109")]),
                            Row(cells=[
                                Cell(variable_key="Publ110", required=True, has_part="Publ210"),
                                Cell(variable_key="Publ210", part_of="Publ110")]),
                            Row(cells=[
                                Cell(variable_key="Publ111", required=True, has_part="Publ211"),
                                Cell(variable_key="Publ211", part_of="Publ111")]),
                            Row(cells=[
                                Cell(variable_key="Publ112", required=True, has_part="Publ212"),
                                Cell(variable_key="Publ212", part_of="Publ112")]),
                            Row(cells=[
                                Cell(variable_key="Publ113", required=True, has_part="Publ213"),
                                Cell(variable_key="Publ213", part_of="Publ113")]),
                            Row(cells=[
                                Cell(variable_key="Publ114", required=True, has_part="Publ214"),
                                Cell(variable_key="Publ214", part_of="Publ114")]),
                            Row(cells=[
                                Cell(variable_key="Publ115", required=True, has_part="Publ215"),
                                Cell(variable_key="Publ215", part_of="Publ115")]),
                            Row(cells=[
                                Cell(variable_key="Publ116", required=True, has_part="Publ216"),
                                Cell(variable_key="Publ216", part_of="Publ116")]),
                            Row(cells=[
                                Cell(variable_key="Publ117", required=True, has_part="Publ217"),
                                Cell(variable_key="Publ217", part_of="Publ117")]),
                            Row(cells=[
                                Cell(variable_key="Publ118", required=True, has_part="Publ218"),
                                Cell(variable_key="Publ218", part_of="Publ118")]),
                            Row(cells=[
                                Cell(variable_key="Publ119", required=True, has_part="Publ219"),
                                Cell(variable_key="Publ219", part_of="Publ119")]),
                            Row(cells=[
                                Cell(variable_key="Publ120", required=True, has_part="Publ220"),
                                Cell(variable_key="Publ220", part_of="Publ120")]),
                            Row(cells=[
                                Cell(variable_key="Publ199",
                                     has_part="Publ299",
                                     sum_of=["Publ101", "Publ102", "Publ103",
                                             "Publ104", "Publ105", "Publ106",
                                             "Publ107", "Publ108", "Publ109",
                                             "Publ110", "Publ111", "Publ112",
                                             "Publ113", "Publ114", "Publ115",
                                             "Publ116", "Publ117", "Publ118",
                                             "Publ119", "Publ120"]),
                                Cell(variable_key="Publ299",
                                     part_of="Publ199",
                                     sum_of=["Publ201", "Publ202", "Publ203",
                                             "Publ204", "Publ205", "Publ206",
                                             "Publ207", "Publ208", "Publ209",
                                             "Publ210", "Publ211", "Publ212",
                                             "Publ213", "Publ214", "Publ215",
                                             "Publ216", "Publ217", "Publ218",
                                             "Publ219", "Publ220"])])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Publkomm")])])]),
            Section(title="Slutligen",
                    groups=[
                        Group(rows=[
                            Row(cells=[Cell(variable_key="SCB01", required=True)]),
                            Row(cells=[Cell(variable_key="SCB02", required=True)])]),
                        Group(rows=[
                            Row(cells=[Cell(variable_key="Alltkomm")])])])])


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
        return _survey_template_base()

    return _default_template_from_survey(survey)

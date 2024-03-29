from libstat.models import Variable


class ReportTemplate:
    @property
    def all_variable_keys(self):
        variable_keys = []
        for group in self.groups:
            for row in group.rows:
                if row.variable_key:
                    if row.variable_key not in variable_keys:
                        variable_keys.append(row.variable_key)
                if row.variable_keys:
                    for variable_key in row.variable_keys:
                        if variable_key not in variable_keys:
                            variable_keys.append(variable_key)
        return variable_keys

    def __init__(self, *args, **kwargs):
        self.groups = kwargs.pop("groups", None)


class Group:
    def __init__(self, *args, **kwargs):
        self.title = kwargs.pop("title", None)
        self.extra = kwargs.pop("extra", None)
        self.rows = kwargs.pop("rows", None)
        self.show_chart = kwargs.pop("show_chart", True)


class Row:
    def compute(self, values):
        if values is None:
            return None
        if None in values:
            return None
        try:
            return self.computation(*values)
            # return apply(self.computation, values)
        except ZeroDivisionError:
            return None

    def __init__(self, *args, **kwargs):
        self.variable_key = kwargs.pop("variable_key", None)
        self.variable_keys = kwargs.pop("variable_keys", None)
        self.computation = kwargs.pop("computation", None)
        self.description = kwargs.pop("description", None)
        self.is_sum = kwargs.pop("is_sum", False)
        self.label_only = kwargs.pop("label_only", False)
        self.show_in_chart = kwargs.pop("show_in_chart", True)
        self.percentage = kwargs.pop("percentage", False)

        if self.description is None and self.variable_key is not None:
            variables = Variable.objects.filter(key=self.variable_key)
            self.description = (
                variables[0].question_part if len(variables) == 1 else None
            )

    @property
    def explanation(self):
        if self.variable_key:
            variables = Variable.objects.filter(key=self.variable_key)
            if len(variables) == 1:
                return variables[0].description
        return None


def report_template_base():
    return ReportTemplate(
        groups=[
            Group(
                title="Organisation",
                rows=[
                    Row(variable_key="BemanService01"),
                    Row(variable_key="Integrerad01"),
                    Row(variable_key="Obeman01"),
                    Row(variable_key="ObemanLan01", show_in_chart=False),
                    Row(variable_key="Bokbuss01", show_in_chart=False),
                    Row(variable_key="BokbussHP01", show_in_chart=False),
                    Row(variable_key="Bokbil01", show_in_chart=False),
                    Row(variable_key="Population01", show_in_chart=False),
                    Row(variable_key="Population02", show_in_chart=False),
                    Row(variable_key="Population03", show_in_chart=False),
                    Row(
                        description="Andel integrerade serviceställen",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Integrerad01", "BemanService01"],
                        percentage=True,
                    ),
                    Row(
                        description="Medelantal utlån till servicesställen där vidare låneregistrering inte sker",
                        computation=(lambda a, b: a / b),
                        variable_keys=["ObemanLan01", "Obeman01"],
                    ),
                ],
            ),
            Group(
                title="Årsverken",
                rows=[
                    Row(variable_key="Arsverke01"),
                    Row(variable_key="Arsverke02"),
                    Row(variable_key="Arsverke03"),
                    Row(variable_key="Arsverke04"),
                    Row(variable_key="Arsverke99", is_sum=True),
                    Row(variable_key="Arsverke05"),
                    Row(
                        description="Andel årsverken för barn och unga",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Arsverke05", "Arsverke99"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel årsverken med bibliotekariekompetens",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Arsverke01", "Arsverke99"],
                        percentage=True,
                    ),
                    Row(
                        description="Antal fysiska besök per årsverke",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Besok01", "Arsverke99"],
                    ),
                    Row(
                        description="Antal aktiva låntagare per årsverke",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Aktiv99", "Arsverke99"],
                    ),
                ],
            ),
            Group(
                title="Personal",
                rows=[
                    Row(variable_key="Personer01"),
                    Row(variable_key="Personer02"),
                    Row(variable_key="Personer99", is_sum=True),
                    Row(
                        description="Andel anställda kvinnor",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Personer01", "Personer99"],
                        percentage=True,
                    ),
                    Row(
                        description="Antal årsverken per anställd",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Arsverke99", "Personer99"],
                    ),
                ],
            ),
            Group(
                title="Ekonomi",
                rows=[
                    Row(variable_key="Utgift01"),
                    Row(variable_key="Utgift02"),
                    Row(variable_key="Utgift03"),
                    Row(variable_key="Utgift04"),
                    Row(variable_key="Utgift05"),
                    Row(variable_key="Utgift06"),
                    Row(variable_key="Utgift99", is_sum=True),
                    Row(variable_key="Utgift07"),
                    Row(
                        description="Andel kostnad för medier av total driftkostnad",
                        computation=(lambda a, b, c: (a + b) / c),
                        variable_keys=["Utgift01", "Utgift02", "Utgift99"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel kostnad för personal av total driftkostnad",
                        computation=(lambda a, b, c: (a + b) / c),
                        variable_keys=["Utgift03", "Utgift04", "Utgift99"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel kostnad för e-medier av total driftskostnad",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utgift02", "Utgift99"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Egengenererade intäkter",
                rows=[
                    Row(variable_key="Intakt01"),
                    Row(variable_key="Intakt02"),
                    Row(variable_key="Intakt03"),
                    Row(variable_key="Intakt99", is_sum=True),
                    Row(
                        description="Andel egengenererade intäkter i förhållande till de totala driftskostnaderna",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Intakt99", "Utgift99"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Fysiskt bestånd",
                extra="Andel av totalt bestånd",
                rows=[
                    Row(
                        variable_key="Bestand101",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand101", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand102",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand102", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand103",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand103", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand104",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand104", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand105",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand105", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand106",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand106", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand107",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand107", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand108",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand108", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand109",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand109", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand110",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand110", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand111",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand111", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand112",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand112", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand113",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand113", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand199",
                        is_sum=True,
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand199", "Bestand199"],
                    ),
                ],
            ),
            Group(
                title="Fysiskt nyförvärv",
                extra="Andel nyförvärv av motsvarande bestånd",
                rows=[
                    Row(
                        variable_key="Bestand201",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand201", "Bestand101"],
                    ),
                    Row(
                        variable_key="Bestand202",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand202", "Bestand102"],
                    ),
                    Row(
                        variable_key="Bestand203",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand203", "Bestand103"],
                    ),
                    Row(
                        variable_key="Bestand204",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand204", "Bestand104"],
                    ),
                    Row(
                        variable_key="Bestand205",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand205", "Bestand105"],
                    ),
                    Row(
                        variable_key="Bestand206",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand206", "Bestand106"],
                    ),
                    Row(
                        variable_key="Bestand207",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand207", "Bestand107"],
                    ),
                    Row(
                        variable_key="Bestand208",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand208", "Bestand108"],
                    ),
                    Row(
                        variable_key="Bestand209",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand209", "Bestand109"],
                    ),
                    Row(
                        variable_key="Bestand210",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand210", "Bestand110"],
                    ),
                    Row(
                        variable_key="Bestand211",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand211", "Bestand111"],
                    ),
                    Row(
                        variable_key="Bestand212",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand212", "Bestand112"],
                    ),
                    Row(
                        variable_key="Bestand213",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand213", "Bestand113"],
                    ),
                    Row(
                        variable_key="Bestand299",
                        is_sum=True,
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand299", "Bestand199"],
                    ),
                ],
            ),
            Group(
                title="Elektroniskt titelbestånd",
                rows=[
                    Row(variable_key="Bestand301"),
                    # Row(variable_key=u"Bestand302"),
                    Row(variable_key="Bestand303"),
                    Row(variable_key="Bestand304"),
                    Row(variable_key="Bestand305"),
                    Row(variable_key="Bestand306"),
                    Row(variable_key="Bestand307"),
                    Row(variable_key="Bestand308"),
                    Row(variable_key="Bestand310"),
                    Row(variable_key="Bestand311"),
                    Row(variable_key="Bestand312"),
                    Row(variable_key="Bestand313"),
                    Row(variable_key="Bestand399", is_sum=True),
                    Row(
                        description="Andel e-bokstitlar av det totala elektroniska titelbeståndet med skriven text",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand301", "Bestand399"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Barnmedier",
                rows=[
                    Row(variable_key="Barn01"),
                    Row(variable_key="Barn02"),
                    Row(variable_key="Barn03"),
                    # Row(description=u"Andel tryckta barnmedier av motsvarande totalbestånd",
                    # computation=(lambda a, b, c: a / (b + c)),
                    # variable_keys=[u"Barn01", u"Bestand101", u"Bestand105"],
                    # percentage=True),
                    Row(
                        description="Andel nyförvärv tryckta barnmedier av motsvarande bestånd",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Barn02", "Barn01"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel utlån tryckta barnmedier av motsvarande bestånd",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Barn03", "Barn01"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="",
                rows=[
                    Row(variable_key="HCG04"),
                    Row(variable_key="Ref05"),
                ],
            ),
            Group(
                title="Personer med läsnedsättning",
                rows=[
                    Row(variable_key="LasnedBest01"),
                    Row(variable_key="LasnedUtlan01"),
                    Row(
                        description="Andel utlån av anpassade medier av motsvarande bestånd",
                        computation=(lambda a, b: a / b),
                        variable_keys=["LasnedUtlan01", "LasnedBest01"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel anpassade medier av totala fysiska beståndet",
                        computation=(lambda a, b: a / b),
                        variable_keys=["LasnedBest01", "Bestand199"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Medier på olika språk",
                rows=[
                    Row(description="Titlar på svenska språket", label_only=True),
                    Row(variable_key="Titlar101"),
                    Row(variable_key="Titlar102"),
                    Row(variable_key="Titlar199", is_sum=True),
                    Row(
                        description="Titlar på nationella minoritetsspråk",
                        label_only=True,
                    ),
                    Row(variable_key="Titlar201"),
                    Row(variable_key="Titlar202"),
                    Row(variable_key="Titlar299", is_sum=True),
                    Row(description="Titlar på utländska språk", label_only=True),
                    Row(variable_key="Titlar301"),
                    Row(variable_key="Titlar302"),
                    Row(variable_key="Titlar399", is_sum=True),
                    Row(
                        description="Totalt antal titlar på olika medietyper",
                        label_only=True,
                    ),
                    Row(variable_key="Titlar497"),
                    Row(variable_key="Titlar498"),
                    Row(variable_key="Titlar499", is_sum=True),
                ],
            ),
            Group(
                title="Elektroniskt bestånd",
                rows=[
                    Row(variable_key="Databas01"),
                    Row(variable_key="Databas02"),
                    Row(variable_key="Databas03"),
                    Row(variable_key="Databas04"),
                    Row(variable_key="Databas05"),
                    Row(variable_key="Databas06"),
                    Row(variable_key="Databas07"),
                    Row(variable_key="Databas08"),
                    Row(variable_key="Databas09"),
                    Row(variable_key="Databas99", is_sum=True),
                ],
            ),
            Group(
                title="Antal initiala lån och omlån fysiskt bestånd",
                rows=[
                    Row(variable_key="Inilan101", show_in_chart=False),
                    Row(variable_key="Inilan102", show_in_chart=False),
                    Row(variable_key="Inilan103", show_in_chart=False),
                    Row(variable_key="Inilan104", show_in_chart=False),
                    Row(variable_key="Inilan105", show_in_chart=False),
                    Row(variable_key="Inilan106", show_in_chart=False),
                    Row(variable_key="Inilan107", show_in_chart=False),
                    Row(variable_key="Inilan108", show_in_chart=False),
                    Row(variable_key="Inilan109", show_in_chart=False),
                    Row(variable_key="Inilan110", show_in_chart=False),
                    Row(variable_key="Inilan111", show_in_chart=False),
                    Row(variable_key="Inilan112", show_in_chart=False),
                    Row(variable_key="Inilan113", show_in_chart=False),
                    Row(variable_key="Inilan199", is_sum=True),
                    Row(
                        description="Andel inititala lån av det totala antalet lån",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Inilan199", "Utlan399"],
                        percentage=True,
                    ),
                    Row(description="", label_only=True),
                    Row(variable_key="Omlan201", show_in_chart=False),
                    Row(variable_key="Omlan202", show_in_chart=False),
                    Row(variable_key="Omlan203", show_in_chart=False),
                    Row(variable_key="Omlan204", show_in_chart=False),
                    Row(variable_key="Omlan205", show_in_chart=False),
                    Row(variable_key="Omlan206", show_in_chart=False),
                    Row(variable_key="Omlan207", show_in_chart=False),
                    Row(variable_key="Omlan208", show_in_chart=False),
                    Row(variable_key="Omlan209", show_in_chart=False),
                    Row(variable_key="Omlan210", show_in_chart=False),
                    Row(variable_key="Omlan211", show_in_chart=False),
                    Row(variable_key="Omlan212", show_in_chart=False),
                    Row(variable_key="Omlan213", show_in_chart=False),
                    Row(variable_key="Omlan299", is_sum=True),
                    Row(
                        description="Andel omlån av det totala antalet lån",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Omlan299", "Utlan399"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Utlån fysiskt bestånd",
                extra="Andel av total fysisk utlåning",
                rows=[
                    Row(
                        variable_key="Utlan301",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan301", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan302",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan302", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan303",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan303", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan304",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan304", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan305",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan305", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan306",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan306", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan307",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan307", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan308",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan308", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan309",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan309", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan310",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan310", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan311",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan311", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan312",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan312", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan313",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan313", "Utlan399"],
                    ),
                    Row(variable_key="Utlan399", is_sum=True),
                ],
            ),
            Group(
                title="Läsning på plats i biblioteket",
                show_chart=False,
                rows=[
                    Row(variable_key="Laslan01"),
                    Row(variable_key="Laslan02"),
                    Row(variable_key="Laslan99"),
                    Row(
                        description="Beräkning lån på plats",
                        computation=(lambda a, b, c: ((a / b) / 2) / c),
                        variable_keys=["Laslan01", "Laslan02", "Open101"],
                    ),
                ],
            ),
            Group(
                title="Fjärrlån",
                rows=[
                    Row(description="Inom Sverige", label_only=True),
                    Row(variable_key="Fjarr101"),
                    Row(variable_key="Fjarr102"),
                    Row(description="Utanför Sverige", label_only=True),
                    Row(variable_key="Fjarr201"),
                    Row(variable_key="Fjarr202"),
                ],
            ),
            Group(
                title="Summering fjärrlån",
                show_chart=False,
                rows=[
                    Row(variable_key="Fjarr397"),
                    Row(variable_key="Fjarr398"),
                    Row(variable_key="Fjarr399", is_sum=True),
                    Row(
                        description="Andel utländska fjärrlån totalt",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Fjarr299", "Fjarr399"],
                        percentage=True,
                    ),
                    Row(
                        description="Nettofjärrinlåning in-ut",
                        computation=(lambda a, b: a - b),
                        variable_keys=["Fjarr397", "Fjarr398"],
                    ),
                ],
            ),
            Group(
                title="Användning av elektroniska samlingar",
                rows=[
                    Row(description="Antal sökningar", label_only=True),
                    Row(variable_key="Elan101"),
                    Row(variable_key="Elan102"),
                    Row(variable_key="Elan103"),
                    Row(variable_key="Elan104"),
                    Row(variable_key="Elan105"),
                    Row(variable_key="Elan106"),
                    Row(variable_key="Elan107"),
                    Row(variable_key="Elan108"),
                    Row(variable_key="Elan109"),
                    Row(variable_key="Elan199", is_sum=True),
                    Row(description="Antal nedladdningar", label_only=True),
                    Row(variable_key="Elan201"),
                    Row(variable_key="Elan202"),
                    Row(variable_key="Elan203"),
                    Row(variable_key="Elan204"),
                    Row(variable_key="Elan205"),
                    Row(variable_key="Elan206"),
                    Row(variable_key="Elan207"),
                    Row(variable_key="Elan208"),
                    Row(variable_key="Elan209"),
                    Row(variable_key="Elan299", is_sum=True),
                    Row(description="Antal nedladdade sektioner", label_only=True),
                    Row(variable_key="Elan301"),
                    Row(variable_key="Elan399", is_sum=True),
                    Row(
                        description="Total användning av de elektroniska samlingarna",
                        computation=(lambda a, b, c: a + b + c),
                        variable_keys=["Elan199", "Elan299", "Elan399"],
                    ),
                ],
            ),
            Group(
                title="Besök",
                rows=[
                    Row(variable_key="Besok01"),
                    Row(variable_key="Besok02"),
                    Row(variable_key="Besok03"),
                    Row(variable_key="Besok04"),
                    Row(variable_key="Besok05"),
                ],
            ),
            Group(
                title="Aktiva användare",
                rows=[
                    Row(variable_key="Aktiv01"),
                    Row(variable_key="Aktiv02"),
                    Row(variable_key="Aktiv04"),
                    Row(variable_key="Aktiv99", is_sum=True),
                    Row(variable_key="Aktiv03"),
                    Row(
                        description="Andel kvinnor som är aktiva låntagare",
                        computation=(lambda a, b: a / (a + b)),
                        variable_keys=["Aktiv01", "Aktiv02"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel barn och unga som är aktiva låntagare",
                        computation=(lambda a, b, c: a / (b + c)),
                        variable_keys=["Aktiv03", "Aktiv01", "Aktiv02"],
                        percentage=True,
                    ),
                    Row(
                        description="Antal fysiska besök per antal aktiva användare",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Besok01", "Aktiv99"],
                    ),
                ],
            ),
            Group(
                title="Resurser",
                rows=[
                    Row(variable_key="Resurs01"),
                    Row(variable_key="Resurs02"),
                    Row(variable_key="Resurs03"),
                    Row(variable_key="Resurs04"),
                    Row(variable_key="Resurs05"),
                    Row(variable_key="Resurs06"),
                    Row(variable_key="Resurs07"),
                    Row(variable_key="Resurs08"),
                    Row(variable_key="Resurs09"),
                    Row(variable_key="Resurs10"),
                    Row(
                        description="Andel publika ytor",
                        computation=(lambda a, b: a / (a + b)),
                        variable_keys=["Resurs09", "Resurs10"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Öppettider",
                rows=[
                    Row(
                        description="Servicestället med de generösaste öppettiderna",
                        label_only=True,
                    ),
                    Row(variable_key="Open101"),
                    Row(variable_key="Open102"),
                    Row(variable_key="Open103"),
                    Row(variable_key="Open104"),
                    Row(variable_key="Open105"),
                    Row(variable_key="Open106"),
                    Row(
                        description="Övriga serviceställen sammantaget", label_only=True
                    ),
                    Row(variable_key="Open201"),
                    Row(variable_key="Open202"),
                    Row(variable_key="Open203"),
                    Row(variable_key="Open204"),
                    Row(variable_key="Open205"),
                    Row(variable_key="Open206"),
                    Row(
                        description="Medelantal öppetdagar per år",
                        computation=(lambda a, b, c: (a + b) / c),
                        variable_keys=["Open201", "Open101", "BemanService01"],
                    ),
                    Row(
                        description="Medelantal öppettimmar alla serviceställen",
                        computation=(lambda a, b, c: (a + b) / c),
                        variable_keys=["Open203", "Open103", "BemanService01"],
                    ),
                    Row(
                        description="Andel öppettimmar med reducerad service",
                        computation=(lambda a, b, c, d: (a + b) / (c + d)),
                        variable_keys=["Open104", "Open204", "Open103", "Open203"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel öppettimmar utanför kontorstid",
                        computation=(lambda a, b, c, d: (a + b) / (c + d)),
                        variable_keys=["Open106", "Open206", "Open103", "Open203"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Service",
                rows=[
                    Row(variable_key="Serv01"),
                    Row(variable_key="Serv02"),
                    Row(variable_key="Serv03"),
                    Row(variable_key="Serv04"),
                    Row(variable_key="Serv05"),
                    Row(variable_key="Serv06"),
                    Row(variable_key="Serv07"),
                ],
            ),
            Group(
                title="Publika aktivitetstillfällen",
                extra="Varav andel tillfällen för barn och unga",
                rows=[
                    Row(
                        variable_key="Publ101",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ201", "Publ101"],
                    ),
                    Row(
                        variable_key="Publ102",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ202", "Publ102"],
                    ),
                    Row(
                        variable_key="Publ103",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ203", "Publ103"],
                    ),
                    Row(
                        variable_key="Publ104",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ204", "Publ104"],
                    ),
                    Row(
                        variable_key="Publ105",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ205", "Publ105"],
                    ),
                    Row(
                        variable_key="Publ106",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ206", "Publ106"],
                    ),
                    Row(
                        variable_key="Publ107",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ207", "Publ107"],
                    ),
                    Row(
                        variable_key="Publ108",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ208", "Publ108"],
                    ),
                    Row(
                        variable_key="Publ109",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ209", "Publ109"],
                    ),
                    Row(
                        variable_key="Publ110",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ210", "Publ110"],
                    ),
                    Row(
                        variable_key="Publ111",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ211", "Publ111"],
                    ),
                    Row(
                        variable_key="Publ112",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ212", "Publ112"],
                    ),
                    Row(
                        variable_key="Publ113",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ213", "Publ113"],
                    ),
                    Row(
                        variable_key="Publ114",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ214", "Publ114"],
                    ),
                    Row(
                        variable_key="Publ115",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ215", "Publ115"],
                    ),
                    Row(
                        variable_key="Publ116",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ216", "Publ116"],
                    ),
                    Row(
                        variable_key="Publ117",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ217", "Publ117"],
                    ),
                    Row(
                        variable_key="Publ118",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ218", "Publ118"],
                    ),
                    Row(
                        variable_key="Publ119",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ219", "Publ119"],
                    ),
                    Row(
                        variable_key="Publ120",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ220", "Publ120"],
                    ),
                    Row(
                        variable_key="Publ199",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ299", "Publ199"],
                        is_sum=True,
                    ),
                    Row(
                        description="Andel publika aktiviteter primärt för barn/unga",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ299", "Publ199"],
                        percentage=True,
                    ),
                    Row(description="", label_only=True),
                    Row(variable_key="Publ201", show_in_chart=False),
                    Row(variable_key="Publ202", show_in_chart=False),
                    Row(variable_key="Publ203", show_in_chart=False),
                    Row(variable_key="Publ204", show_in_chart=False),
                    Row(variable_key="Publ205", show_in_chart=False),
                    Row(variable_key="Publ206", show_in_chart=False),
                    Row(variable_key="Publ207", show_in_chart=False),
                    Row(variable_key="Publ208", show_in_chart=False),
                    Row(variable_key="Publ209", show_in_chart=False),
                    Row(variable_key="Publ210", show_in_chart=False),
                    Row(variable_key="Publ211", show_in_chart=False),
                    Row(variable_key="Publ212", show_in_chart=False),
                    Row(variable_key="Publ213", show_in_chart=False),
                    Row(variable_key="Publ214", show_in_chart=False),
                    Row(variable_key="Publ215", show_in_chart=False),
                    Row(variable_key="Publ216", show_in_chart=False),
                    Row(variable_key="Publ217", show_in_chart=False),
                    Row(variable_key="Publ218", show_in_chart=False),
                    Row(variable_key="Publ219", show_in_chart=False),
                    Row(variable_key="Publ220", show_in_chart=False),
                    Row(variable_key="Publ299", is_sum=True, show_in_chart=False),
                ],
            ),
        ]
    )


def report_template_base_with_target_group_calculations():
    return ReportTemplate(
        groups=[
            Group(
                title="Organisation",
                rows=[
                    Row(variable_key="BemanService01"),
                    Row(variable_key="Integrerad01"),
                    Row(variable_key="Obeman01"),
                    Row(variable_key="ObemanLan01", show_in_chart=False),
                    Row(variable_key="Bokbuss01", show_in_chart=False),
                    Row(variable_key="BokbussHP01", show_in_chart=False),
                    Row(variable_key="Bokbil01", show_in_chart=False),
                    Row(variable_key="Population01", show_in_chart=False),
                    Row(variable_key="Population02", show_in_chart=False),
                    Row(variable_key="Population03", show_in_chart=False),
                    Row(
                        description="Andel integrerade serviceställen",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Integrerad01", "BemanService01"],
                        percentage=True,
                    ),
                    Row(
                        description="Medelantal utlån till servicesställen där vidare låneregistrering inte sker",
                        computation=(lambda a, b: a / b),
                        variable_keys=["ObemanLan01", "Obeman01"],
                    ),
                ],
            ),
            Group(
                title="Årsverken",
                rows=[
                    Row(variable_key="Arsverke01"),
                    Row(variable_key="Arsverke02"),
                    Row(variable_key="Arsverke03"),
                    Row(variable_key="Arsverke04"),
                    Row(variable_key="Arsverke99", is_sum=True),
                    Row(variable_key="Arsverke05"),
                    Row(
                        description="Andel årsverken för barn och unga",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Arsverke05", "Arsverke99"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel årsverken med bibliotekariekompetens",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Arsverke01", "Arsverke99"],
                        percentage=True,
                    ),
                    Row(
                        description="Antal årsverken per 100 personer i målgruppen",
                        computation=(lambda a, b: a / (b / 100)),
                        variable_keys=["Arsverke99", "Population02"],
                    ),
                    Row(
                        description="Antal fysiska besök per årsverke",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Besok01", "Arsverke99"],
                    ),
                    Row(
                        description="Antal aktiva låntagare per årsverke",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Aktiv99", "Arsverke99"],
                    ),
                ],
            ),
            Group(
                title="Personal",
                rows=[
                    Row(variable_key="Personer01"),
                    Row(variable_key="Personer02"),
                    Row(variable_key="Personer99", is_sum=True),
                    Row(
                        description="Andel anställda kvinnor",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Personer01", "Personer99"],
                        percentage=True,
                    ),
                    Row(
                        description="Antal årsverken per anställd",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Arsverke99", "Personer99"],
                    ),
                ],
            ),
            Group(
                title="Ekonomi",
                rows=[
                    Row(variable_key="Utgift01"),
                    Row(variable_key="Utgift02"),
                    Row(variable_key="Utgift03"),
                    Row(variable_key="Utgift04"),
                    Row(variable_key="Utgift05"),
                    Row(variable_key="Utgift06"),
                    Row(variable_key="Utgift99", is_sum=True),
                    Row(variable_key="Utgift07"),
                    Row(
                        description="Mediekostnad per person i målgruppen",
                        computation=(lambda a, b, c: (a + b) / c),
                        variable_keys=["Utgift01", "Utgift02", "Population02"],
                    ),
                    Row(
                        description="Total driftkostnad per person i målgruppen",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utgift99", "Population02"],
                    ),
                    Row(
                        description="Andel kostnad för medier av total driftkostnad",
                        computation=(lambda a, b, c: (a + b) / c),
                        variable_keys=["Utgift01", "Utgift02", "Utgift99"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel kostnad för personal av total driftkostnad",
                        computation=(lambda a, b, c: (a + b) / c),
                        variable_keys=["Utgift03", "Utgift04", "Utgift99"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel kostnad för e-medier av total driftskostnad",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utgift02", "Utgift99"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Egengenererade intäkter",
                rows=[
                    Row(variable_key="Intakt01"),
                    Row(variable_key="Intakt02"),
                    Row(variable_key="Intakt03"),
                    Row(variable_key="Intakt99", is_sum=True),
                    Row(
                        description="Andel egengenererade intäkter i förhållande till de totala driftskostnaderna",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Intakt99", "Utgift99"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Fysiskt bestånd",
                extra="Andel av totalt bestånd",
                rows=[
                    Row(
                        variable_key="Bestand101",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand101", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand102",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand102", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand103",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand103", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand104",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand104", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand105",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand105", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand106",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand106", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand107",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand107", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand108",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand108", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand109",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand109", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand110",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand110", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand111",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand111", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand112",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand112", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand113",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand113", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand199",
                        is_sum=True,
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand199", "Bestand199"],
                    ),
                ],
            ),
            Group(
                title="Fysiskt nyförvärv",
                extra="Andel nyförvärv av motsvarande bestånd",
                rows=[
                    Row(
                        variable_key="Bestand201",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand201", "Bestand101"],
                    ),
                    Row(
                        variable_key="Bestand202",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand202", "Bestand102"],
                    ),
                    Row(
                        variable_key="Bestand203",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand203", "Bestand103"],
                    ),
                    Row(
                        variable_key="Bestand204",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand204", "Bestand104"],
                    ),
                    Row(
                        variable_key="Bestand205",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand205", "Bestand105"],
                    ),
                    Row(
                        variable_key="Bestand206",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand206", "Bestand106"],
                    ),
                    Row(
                        variable_key="Bestand207",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand207", "Bestand107"],
                    ),
                    Row(
                        variable_key="Bestand208",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand208", "Bestand108"],
                    ),
                    Row(
                        variable_key="Bestand209",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand209", "Bestand109"],
                    ),
                    Row(
                        variable_key="Bestand210",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand210", "Bestand110"],
                    ),
                    Row(
                        variable_key="Bestand211",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand211", "Bestand111"],
                    ),
                    Row(
                        variable_key="Bestand212",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand212", "Bestand112"],
                    ),
                    Row(
                        variable_key="Bestand213",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand213", "Bestand113"],
                    ),
                    Row(
                        variable_key="Bestand299",
                        is_sum=True,
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand299", "Bestand199"],
                    ),
                ],
            ),
            Group(
                title="Elektroniskt titelbestånd",
                rows=[
                    Row(variable_key="Bestand301"),
                    # Row(variable_key=u"Bestand302"),
                    Row(variable_key="Bestand303"),
                    Row(variable_key="Bestand304"),
                    Row(variable_key="Bestand305"),
                    Row(variable_key="Bestand306"),
                    Row(variable_key="Bestand307"),
                    Row(variable_key="Bestand308"),
                    Row(variable_key="Bestand310"),
                    Row(variable_key="Bestand311"),
                    Row(variable_key="Bestand312"),
                    Row(variable_key="Bestand313"),
                    Row(variable_key="Bestand399", is_sum=True),
                    Row(
                        description="Andel e-bokstitlar av det totala elektroniska titelbeståndet med skriven text",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand301", "Bestand399"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Barnmedier",
                rows=[
                    Row(variable_key="Barn01"),
                    Row(variable_key="Barn02"),
                    Row(variable_key="Barn03"),
                    # Row(description=u"Andel tryckta barnmedier av motsvarande totalbestånd",
                    # computation=(lambda a, b, c: a / (b + c)),
                    # variable_keys=[u"Barn01", u"Bestand101", u"Bestand105"],
                    # percentage=True),
                    Row(
                        description="Andel nyförvärv tryckta barnmedier av motsvarande bestånd",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Barn02", "Barn01"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel utlån tryckta barnmedier av motsvarande bestånd",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Barn03", "Barn01"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="",
                rows=[
                    Row(variable_key="HCG04"),
                    Row(variable_key="Ref05"),
                ],
            ),
            Group(
                title="Personer med läsnedsättning",
                rows=[
                    Row(variable_key="LasnedBest01"),
                    Row(variable_key="LasnedUtlan01"),
                    Row(
                        description="Andel utlån av anpassade medier av motsvarande bestånd",
                        computation=(lambda a, b: a / b),
                        variable_keys=["LasnedUtlan01", "LasnedBest01"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel anpassade medier av totala fysiska beståndet",
                        computation=(lambda a, b: a / b),
                        variable_keys=["LasnedBest01", "Bestand199"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Medier på olika språk",
                rows=[
                    Row(description="Titlar på svenska språket", label_only=True),
                    Row(variable_key="Titlar101"),
                    Row(variable_key="Titlar102"),
                    Row(variable_key="Titlar199", is_sum=True),
                    Row(
                        description="Titlar på nationella minoritetsspråk",
                        label_only=True,
                    ),
                    Row(variable_key="Titlar201"),
                    Row(variable_key="Titlar202"),
                    Row(variable_key="Titlar299", is_sum=True),
                    Row(description="Titlar på utländska språk", label_only=True),
                    Row(variable_key="Titlar301"),
                    Row(variable_key="Titlar302"),
                    Row(variable_key="Titlar399", is_sum=True),
                    Row(
                        description="Totalt antal titlar på olika medietyper",
                        label_only=True,
                    ),
                    Row(variable_key="Titlar497"),
                    Row(variable_key="Titlar498"),
                    Row(variable_key="Titlar499", is_sum=True),
                ],
            ),
            Group(
                title="Elektroniskt bestånd",
                rows=[
                    Row(variable_key="Databas01"),
                    Row(variable_key="Databas02"),
                    Row(variable_key="Databas03"),
                    Row(variable_key="Databas04"),
                    Row(variable_key="Databas05"),
                    Row(variable_key="Databas06"),
                    Row(variable_key="Databas07"),
                    Row(variable_key="Databas08"),
                    Row(variable_key="Databas09"),
                    Row(variable_key="Databas99", is_sum=True),
                ],
            ),
            Group(
                title="Antal initiala lån och omlån fysiskt bestånd",
                rows=[
                    Row(variable_key="Inilan101", show_in_chart=False),
                    Row(variable_key="Inilan102", show_in_chart=False),
                    Row(variable_key="Inilan103", show_in_chart=False),
                    Row(variable_key="Inilan104", show_in_chart=False),
                    Row(variable_key="Inilan105", show_in_chart=False),
                    Row(variable_key="Inilan106", show_in_chart=False),
                    Row(variable_key="Inilan107", show_in_chart=False),
                    Row(variable_key="Inilan108", show_in_chart=False),
                    Row(variable_key="Inilan109", show_in_chart=False),
                    Row(variable_key="Inilan110", show_in_chart=False),
                    Row(variable_key="Inilan111", show_in_chart=False),
                    Row(variable_key="Inilan112", show_in_chart=False),
                    Row(variable_key="Inilan113", show_in_chart=False),
                    Row(variable_key="Inilan199", is_sum=True),
                    Row(
                        description="Andel inititala lån av det totala antalet lån",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Inilan199", "Utlan399"],
                        percentage=True,
                    ),
                    Row(description="", label_only=True),
                    Row(variable_key="Omlan201", show_in_chart=False),
                    Row(variable_key="Omlan202", show_in_chart=False),
                    Row(variable_key="Omlan203", show_in_chart=False),
                    Row(variable_key="Omlan204", show_in_chart=False),
                    Row(variable_key="Omlan205", show_in_chart=False),
                    Row(variable_key="Omlan206", show_in_chart=False),
                    Row(variable_key="Omlan207", show_in_chart=False),
                    Row(variable_key="Omlan208", show_in_chart=False),
                    Row(variable_key="Omlan209", show_in_chart=False),
                    Row(variable_key="Omlan210", show_in_chart=False),
                    Row(variable_key="Omlan211", show_in_chart=False),
                    Row(variable_key="Omlan212", show_in_chart=False),
                    Row(variable_key="Omlan213", show_in_chart=False),
                    Row(variable_key="Omlan299", is_sum=True),
                    Row(
                        description="Andel omlån av det totala antalet lån",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Omlan299", "Utlan399"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Utlån fysiskt bestånd",
                extra="Andel av total fysisk utlåning",
                rows=[
                    Row(
                        variable_key="Utlan301",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan301", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan302",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan302", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan303",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan303", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan304",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan304", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan305",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan305", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan306",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan306", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan307",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan307", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan308",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan308", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan309",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan309", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan310",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan310", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan311",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan311", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan312",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan312", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan313",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan313", "Utlan399"],
                    ),
                    Row(variable_key="Utlan399", is_sum=True),
                    Row(
                        description="Antal utlån per person i målgruppen",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan399", "Population02"],
                    ),
                    Row(
                        description="Fysiska böcker med skriven text per person i målgruppen",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan301", "Population02"],
                    ),
                ],
            ),
            Group(
                title="Läsning på plats i biblioteket",
                show_chart=False,
                rows=[
                    Row(variable_key="Laslan01"),
                    Row(variable_key="Laslan02"),
                    Row(variable_key="Laslan99"),
                    Row(
                        description="Beräkning lån på plats",
                        computation=(lambda a, b, c: ((a / b) / 2) / c),
                        variable_keys=["Laslan01", "Laslan02", "Open101"],
                    ),
                ],
            ),
            Group(
                title="Fjärrlån",
                rows=[
                    Row(description="Inom Sverige", label_only=True),
                    Row(variable_key="Fjarr101"),
                    Row(variable_key="Fjarr102"),
                    Row(description="Utanför Sverige", label_only=True),
                    Row(variable_key="Fjarr201"),
                    Row(variable_key="Fjarr202"),
                ],
            ),
            Group(
                title="Summering fjärrlån",
                show_chart=False,
                rows=[
                    Row(variable_key="Fjarr397"),
                    Row(variable_key="Fjarr398"),
                    Row(variable_key="Fjarr399", is_sum=True),
                    Row(
                        description="Andel utländska fjärrlån totalt",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Fjarr299", "Fjarr399"],
                        percentage=True,
                    ),
                    Row(
                        description="Nettofjärrinlåning in-ut",
                        computation=(lambda a, b: a - b),
                        variable_keys=["Fjarr397", "Fjarr398"],
                    ),
                ],
            ),
            Group(
                title="Användning av elektroniska samlingar",
                rows=[
                    Row(description="Antal sökningar", label_only=True),
                    Row(variable_key="Elan101"),
                    Row(variable_key="Elan102"),
                    Row(variable_key="Elan103"),
                    Row(variable_key="Elan104"),
                    Row(variable_key="Elan105"),
                    Row(variable_key="Elan106"),
                    Row(variable_key="Elan107"),
                    Row(variable_key="Elan108"),
                    Row(variable_key="Elan109"),
                    Row(variable_key="Elan199", is_sum=True),
                    Row(description="Antal nedladdningar", label_only=True),
                    Row(variable_key="Elan201"),
                    Row(variable_key="Elan202"),
                    Row(variable_key="Elan203"),
                    Row(variable_key="Elan204"),
                    Row(variable_key="Elan205"),
                    Row(variable_key="Elan206"),
                    Row(variable_key="Elan207"),
                    Row(variable_key="Elan208"),
                    Row(variable_key="Elan209"),
                    Row(variable_key="Elan299", is_sum=True),
                    Row(description="Antal nedladdade sektioner", label_only=True),
                    Row(variable_key="Elan301"),
                    Row(variable_key="Elan399", is_sum=True),
                    Row(
                        description="Total användning av de elektroniska samlingarna",
                        computation=(lambda a, b, c: a + b + c),
                        variable_keys=["Elan199", "Elan299", "Elan399"],
                    ),
                ],
            ),
            Group(
                title="Besök",
                rows=[
                    Row(variable_key="Besok01"),
                    Row(variable_key="Besok02"),
                    Row(variable_key="Besok03"),
                    Row(variable_key="Besok04"),
                    Row(variable_key="Besok05"),
                ],
            ),
            Group(
                title="Aktiva användare",
                rows=[
                    Row(variable_key="Aktiv01"),
                    Row(variable_key="Aktiv02"),
                    Row(variable_key="Aktiv04"),
                    Row(variable_key="Aktiv99", is_sum=True),
                    Row(variable_key="Aktiv03"),
                    Row(
                        description="Andel kvinnor som är aktiva låntagare",
                        computation=(lambda a, b: a / (a + b)),
                        variable_keys=["Aktiv01", "Aktiv02"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel barn och unga som är aktiva låntagare",
                        computation=(lambda a, b, c: a / (b + c)),
                        variable_keys=["Aktiv03", "Aktiv01", "Aktiv02"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel aktiva användare per person i målgruppen",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Aktiv99", "Population02"],
                        percentage=True,
                    ),
                    Row(
                        description="Antal fysiska besök per antal aktiva användare",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Besok01", "Aktiv99"],
                    ),
                ],
            ),
            Group(
                title="Resurser",
                rows=[
                    Row(variable_key="Resurs01"),
                    Row(variable_key="Resurs02"),
                    Row(variable_key="Resurs03"),
                    Row(variable_key="Resurs04"),
                    Row(variable_key="Resurs05"),
                    Row(variable_key="Resurs06"),
                    Row(variable_key="Resurs07"),
                    Row(variable_key="Resurs08"),
                    Row(variable_key="Resurs09"),
                    Row(variable_key="Resurs10"),
                    Row(
                        description="Andel publika ytor",
                        computation=(lambda a, b: a / (a + b)),
                        variable_keys=["Resurs09", "Resurs10"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Öppettider",
                rows=[
                    Row(
                        description="Servicestället med de generösaste öppettiderna",
                        label_only=True,
                    ),
                    Row(variable_key="Open101"),
                    Row(variable_key="Open102"),
                    Row(variable_key="Open103"),
                    Row(variable_key="Open104"),
                    Row(variable_key="Open105"),
                    Row(variable_key="Open106"),
                    Row(
                        description="Övriga serviceställen sammantaget", label_only=True
                    ),
                    Row(variable_key="Open201"),
                    Row(variable_key="Open202"),
                    Row(variable_key="Open203"),
                    Row(variable_key="Open204"),
                    Row(variable_key="Open205"),
                    Row(variable_key="Open206"),
                    Row(
                        description="Medelantal öppetdagar per år",
                        computation=(lambda a, b, c: (a + b) / c),
                        variable_keys=["Open201", "Open101", "BemanService01"],
                    ),
                    Row(
                        description="Medelantal öppettimmar alla serviceställen",
                        computation=(lambda a, b, c: (a + b) / c),
                        variable_keys=["Open203", "Open103", "BemanService01"],
                    ),
                    Row(
                        description="Andel öppettimmar med reducerad service",
                        computation=(lambda a, b, c, d: (a + b) / (c + d)),
                        variable_keys=["Open104", "Open204", "Open103", "Open203"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel öppettimmar utanför kontorstid",
                        computation=(lambda a, b, c, d: (a + b) / (c + d)),
                        variable_keys=["Open106", "Open206", "Open103", "Open203"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Service",
                rows=[
                    Row(variable_key="Serv01"),
                    Row(variable_key="Serv02"),
                    Row(variable_key="Serv03"),
                    Row(variable_key="Serv04"),
                    Row(variable_key="Serv05"),
                    Row(variable_key="Serv06"),
                    Row(variable_key="Serv07"),
                ],
            ),
            Group(
                title="Publika aktivitetstillfällen",
                extra="Varav andel tillfällen för barn och unga",
                rows=[
                    Row(
                        variable_key="Publ101",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ201", "Publ101"],
                    ),
                    Row(
                        variable_key="Publ102",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ202", "Publ102"],
                    ),
                    Row(
                        variable_key="Publ103",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ203", "Publ103"],
                    ),
                    Row(
                        variable_key="Publ104",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ204", "Publ104"],
                    ),
                    Row(
                        variable_key="Publ105",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ205", "Publ105"],
                    ),
                    Row(
                        variable_key="Publ106",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ206", "Publ106"],
                    ),
                    Row(
                        variable_key="Publ107",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ207", "Publ107"],
                    ),
                    Row(
                        variable_key="Publ108",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ208", "Publ108"],
                    ),
                    Row(
                        variable_key="Publ109",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ209", "Publ109"],
                    ),
                    Row(
                        variable_key="Publ110",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ210", "Publ110"],
                    ),
                    Row(
                        variable_key="Publ111",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ211", "Publ111"],
                    ),
                    Row(
                        variable_key="Publ112",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ212", "Publ112"],
                    ),
                    Row(
                        variable_key="Publ113",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ213", "Publ113"],
                    ),
                    Row(
                        variable_key="Publ114",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ214", "Publ114"],
                    ),
                    Row(
                        variable_key="Publ115",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ215", "Publ115"],
                    ),
                    Row(
                        variable_key="Publ116",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ216", "Publ116"],
                    ),
                    Row(
                        variable_key="Publ117",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ217", "Publ117"],
                    ),
                    Row(
                        variable_key="Publ118",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ218", "Publ118"],
                    ),
                    Row(
                        variable_key="Publ119",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ219", "Publ119"],
                    ),
                    Row(
                        variable_key="Publ120",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ220", "Publ120"],
                    ),
                    Row(
                        variable_key="Publ199",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ299", "Publ199"],
                        is_sum=True,
                    ),
                    Row(
                        description="Andel publika aktiviteter primärt för barn/unga",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ299", "Publ199"],
                        percentage=True,
                    ),
                    Row(description="", label_only=True),
                    Row(variable_key="Publ201", show_in_chart=False),
                    Row(variable_key="Publ202", show_in_chart=False),
                    Row(variable_key="Publ203", show_in_chart=False),
                    Row(variable_key="Publ204", show_in_chart=False),
                    Row(variable_key="Publ205", show_in_chart=False),
                    Row(variable_key="Publ206", show_in_chart=False),
                    Row(variable_key="Publ207", show_in_chart=False),
                    Row(variable_key="Publ208", show_in_chart=False),
                    Row(variable_key="Publ209", show_in_chart=False),
                    Row(variable_key="Publ210", show_in_chart=False),
                    Row(variable_key="Publ211", show_in_chart=False),
                    Row(variable_key="Publ212", show_in_chart=False),
                    Row(variable_key="Publ213", show_in_chart=False),
                    Row(variable_key="Publ214", show_in_chart=False),
                    Row(variable_key="Publ215", show_in_chart=False),
                    Row(variable_key="Publ216", show_in_chart=False),
                    Row(variable_key="Publ217", show_in_chart=False),
                    Row(variable_key="Publ218", show_in_chart=False),
                    Row(variable_key="Publ219", show_in_chart=False),
                    Row(variable_key="Publ220", show_in_chart=False),
                    Row(variable_key="Publ299", is_sum=True, show_in_chart=False),
                ],
            ),
        ]
    )


def report_template_base_with_municipality_calculations():
    return ReportTemplate(
        groups=[
            Group(
                title="Organisation",
                rows=[
                    Row(variable_key="BemanService01"),
                    Row(variable_key="Integrerad01"),
                    Row(variable_key="Obeman01"),
                    Row(variable_key="ObemanLan01", show_in_chart=False),
                    Row(variable_key="Bokbuss01", show_in_chart=False),
                    Row(variable_key="BokbussHP01", show_in_chart=False),
                    Row(variable_key="Bokbil01", show_in_chart=False),
                    Row(variable_key="Population01", show_in_chart=False),
                    Row(variable_key="Population02", show_in_chart=False),
                    Row(variable_key="Population03", show_in_chart=False),
                    Row(
                        description="Antal bemannade serviceställen per 1000 invånare",
                        computation=(lambda a, b: a / (b / 1000)),
                        variable_keys=["BemanService01", "Population01"],
                    ),
                    Row(
                        description="Andel integrerade serviceställen",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Integrerad01", "BemanService01"],
                        percentage=True,
                    ),
                    Row(
                        description="Medelantal utlån till servicesställen där vidare låneregistrering inte sker",
                        computation=(lambda a, b: a / b),
                        variable_keys=["ObemanLan01", "Obeman01"],
                    ),
                ],
            ),
            Group(
                title="Årsverken",
                rows=[
                    Row(variable_key="Arsverke01"),
                    Row(variable_key="Arsverke02"),
                    Row(variable_key="Arsverke03"),
                    Row(variable_key="Arsverke04"),
                    Row(variable_key="Arsverke99", is_sum=True),
                    Row(variable_key="Arsverke05"),
                    Row(
                        description="Andel årsverken för barn och unga",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Arsverke05", "Arsverke99"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel årsverken med bibliotekariekompetens",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Arsverke01", "Arsverke99"],
                        percentage=True,
                    ),
                    Row(
                        description="Antal  årsverken per 1000 invånare",
                        computation=(lambda a, b: a / (b / 1000)),
                        variable_keys=["Arsverke99", "Population01"],
                    ),
                    Row(
                        description="Antal fysiska besök per årsverke",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Besok01", "Arsverke99"],
                    ),
                    Row(
                        description="Antal aktiva låntagare per årsverke",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Aktiv99", "Arsverke99"],
                    ),
                ],
            ),
            Group(
                title="Personal",
                rows=[
                    Row(variable_key="Personer01"),
                    Row(variable_key="Personer02"),
                    Row(variable_key="Personer99", is_sum=True),
                    Row(
                        description="Andel anställda kvinnor",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Personer01", "Personer99"],
                        percentage=True,
                    ),
                    Row(
                        description="Antal årsverken per anställd",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Arsverke99", "Personer99"],
                    ),
                ],
            ),
            Group(
                title="Ekonomi",
                rows=[
                    Row(variable_key="Utgift01"),
                    Row(variable_key="Utgift02"),
                    Row(variable_key="Utgift03"),
                    Row(variable_key="Utgift04"),
                    Row(variable_key="Utgift05"),
                    Row(variable_key="Utgift06"),
                    Row(variable_key="Utgift99", is_sum=True),
                    Row(variable_key="Utgift07"),
                    Row(
                        description="Mediekostnad per invånare i kommunen",
                        computation=(lambda a, b, c: (a + b) / c),
                        variable_keys=["Utgift01", "Utgift02", "Population01"],
                    ),
                    Row(
                        description="Total driftkostnad per invånare i kommunen",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utgift99", "Population01"],
                    ),
                    Row(
                        description="Andel kostnad för medier av total driftkostnad",
                        computation=(lambda a, b, c: (a + b) / c),
                        variable_keys=["Utgift01", "Utgift02", "Utgift99"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel kostnad för personal av total driftkostnad",
                        computation=(lambda a, b, c: (a + b) / c),
                        variable_keys=["Utgift03", "Utgift04", "Utgift99"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel kostnad för e-medier av total driftskostnad",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utgift02", "Utgift99"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Egengenererade intäkter",
                rows=[
                    Row(variable_key="Intakt01"),
                    Row(variable_key="Intakt02"),
                    Row(variable_key="Intakt03"),
                    Row(variable_key="Intakt99", is_sum=True),
                    Row(
                        description="Andel egengenererade intäkter i förhållande till de totala driftskostnaderna",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Intakt99", "Utgift99"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Fysiskt bestånd",
                extra="Andel av totalt bestånd",
                rows=[
                    Row(
                        variable_key="Bestand101",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand101", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand102",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand102", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand103",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand103", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand104",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand104", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand105",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand105", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand106",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand106", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand107",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand107", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand108",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand108", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand109",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand109", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand110",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand110", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand111",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand111", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand112",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand112", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand113",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand113", "Bestand199"],
                    ),
                    Row(
                        variable_key="Bestand199",
                        is_sum=True,
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand199", "Bestand199"],
                    ),
                    Row(
                        description="Totalt fysiskt mediebestånd per invånare",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand199", "Population01"],
                    ),
                    Row(
                        description="Antal fysiska böcker med skriven text per invånare i beståndet",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand101", "Population01"],
                    ),
                ],
            ),
            Group(
                title="Fysiskt nyförvärv",
                extra="Andel nyförvärv av motsvarande bestånd",
                rows=[
                    Row(
                        variable_key="Bestand201",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand201", "Bestand101"],
                    ),
                    Row(
                        variable_key="Bestand202",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand202", "Bestand102"],
                    ),
                    Row(
                        variable_key="Bestand203",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand203", "Bestand103"],
                    ),
                    Row(
                        variable_key="Bestand204",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand204", "Bestand104"],
                    ),
                    Row(
                        variable_key="Bestand205",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand205", "Bestand105"],
                    ),
                    Row(
                        variable_key="Bestand206",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand206", "Bestand106"],
                    ),
                    Row(
                        variable_key="Bestand207",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand207", "Bestand107"],
                    ),
                    Row(
                        variable_key="Bestand208",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand208", "Bestand108"],
                    ),
                    Row(
                        variable_key="Bestand209",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand209", "Bestand109"],
                    ),
                    Row(
                        variable_key="Bestand210",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand210", "Bestand110"],
                    ),
                    Row(
                        variable_key="Bestand211",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand211", "Bestand111"],
                    ),
                    Row(
                        variable_key="Bestand212",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand212", "Bestand112"],
                    ),
                    Row(
                        variable_key="Bestand213",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand213", "Bestand113"],
                    ),
                    Row(
                        variable_key="Bestand299",
                        is_sum=True,
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand299", "Bestand199"],
                    ),
                    Row(
                        description="Antal fysiska  nyförvärv per 1000 invånare (ej tidn.tidskr.)",
                        computation=(
                            lambda a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11: (
                                a1 + a2 + a3 + a4 + a5 + a6 + a7 + a8 + a9 + a10
                            )
                            / (a11 / 1000)
                        ),
                        variable_keys=[
                            "Bestand101",
                            "Bestand103",
                            "Bestand104",
                            "Bestand107",
                            "Bestand108",
                            "Bestand109",
                            "Bestand110",
                            "Bestand111",
                            "Bestand112",
                            "Bestand113",
                            "Population01",
                        ],
                    ),
                ],
            ),
            Group(
                title="Elektroniskt titelbestånd",
                rows=[
                    Row(variable_key="Bestand301"),
                    # Row(variable_key=u"Bestand302"),
                    Row(variable_key="Bestand303"),
                    Row(variable_key="Bestand304"),
                    Row(variable_key="Bestand305"),
                    Row(variable_key="Bestand306"),
                    Row(variable_key="Bestand307"),
                    Row(variable_key="Bestand308"),
                    Row(variable_key="Bestand310"),
                    Row(variable_key="Bestand311"),
                    Row(variable_key="Bestand312"),
                    Row(variable_key="Bestand313"),
                    Row(variable_key="Bestand399", is_sum=True),
                    Row(
                        description="Andel e-bokstitlar av det totala elektroniska titelbeståndet med skriven text",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Bestand301", "Bestand399"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Barnmedier",
                rows=[
                    Row(variable_key="Barn01"),
                    Row(variable_key="Barn02"),
                    Row(variable_key="Barn03"),
                    Row(
                        description="Antal bestånd barnböcker per barn",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Barn01", "Population03"],
                    ),
                    # Row(description=u"Andel tryckta barnmedier av motsvarande totalbestånd",
                    # computation=(lambda a, b, c: a / (b + c)),
                    # variable_keys=[u"Barn01", u"Bestand101", u"Bestand105"],
                    # percentage=True),
                    Row(
                        description="Andel nyförvärv tryckta barnmedier av motsvarande bestånd",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Barn02", "Barn01"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel utlån tryckta barnmedier av motsvarande bestånd",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Barn03", "Barn01"],
                        percentage=True,
                    ),
                    Row(
                        description="Antal barnutlån per barninvånare",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Barn03", "Population03"],
                    ),
                ],
            ),
            Group(
                title="",
                rows=[
                    Row(variable_key="HCG04"),
                    Row(variable_key="Ref05"),
                ],
            ),
            Group(
                title="Personer med läsnedsättning",
                rows=[
                    Row(variable_key="LasnedBest01"),
                    Row(variable_key="LasnedUtlan01"),
                    Row(
                        description="Andel utlån av anpassade medier av motsvarande bestånd",
                        computation=(lambda a, b: a / b),
                        variable_keys=["LasnedUtlan01", "LasnedBest01"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel anpassade medier av totala fysiska beståndet",
                        computation=(lambda a, b: a / b),
                        variable_keys=["LasnedBest01", "Bestand199"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Medier på olika språk",
                rows=[
                    Row(description="Titlar på svenska språket", label_only=True),
                    Row(variable_key="Titlar101"),
                    Row(variable_key="Titlar102"),
                    Row(variable_key="Titlar199", is_sum=True),
                    Row(
                        description="Titlar på nationella minoritetsspråk",
                        label_only=True,
                    ),
                    Row(variable_key="Titlar201"),
                    Row(variable_key="Titlar202"),
                    Row(variable_key="Titlar299", is_sum=True),
                    Row(description="Titlar på utländska språk", label_only=True),
                    Row(variable_key="Titlar301"),
                    Row(variable_key="Titlar302"),
                    Row(variable_key="Titlar399", is_sum=True),
                    Row(
                        description="Totalt antal titlar på olika medietyper",
                        label_only=True,
                    ),
                    Row(variable_key="Titlar497"),
                    Row(variable_key="Titlar498"),
                    Row(variable_key="Titlar499", is_sum=True),
                ],
            ),
            Group(
                title="Elektroniskt bestånd",
                rows=[
                    Row(variable_key="Databas01"),
                    Row(variable_key="Databas02"),
                    Row(variable_key="Databas03"),
                    Row(variable_key="Databas04"),
                    Row(variable_key="Databas05"),
                    Row(variable_key="Databas06"),
                    Row(variable_key="Databas07"),
                    Row(variable_key="Databas08"),
                    Row(variable_key="Databas09"),
                    Row(variable_key="Databas99", is_sum=True),
                ],
            ),
            Group(
                title="Antal initiala lån och omlån fysiskt bestånd",
                rows=[
                    Row(variable_key="Inilan101", show_in_chart=False),
                    Row(variable_key="Inilan102", show_in_chart=False),
                    Row(variable_key="Inilan103", show_in_chart=False),
                    Row(variable_key="Inilan104", show_in_chart=False),
                    Row(variable_key="Inilan105", show_in_chart=False),
                    Row(variable_key="Inilan106", show_in_chart=False),
                    Row(variable_key="Inilan107", show_in_chart=False),
                    Row(variable_key="Inilan108", show_in_chart=False),
                    Row(variable_key="Inilan109", show_in_chart=False),
                    Row(variable_key="Inilan110", show_in_chart=False),
                    Row(variable_key="Inilan111", show_in_chart=False),
                    Row(variable_key="Inilan112", show_in_chart=False),
                    Row(variable_key="Inilan113", show_in_chart=False),
                    Row(variable_key="Inilan199", is_sum=True),
                    Row(
                        description="Andel inititala lån av det totala antalet lån",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Inilan199", "Utlan399"],
                        percentage=True,
                    ),
                    Row(description="", label_only=True),
                    Row(variable_key="Omlan201", show_in_chart=False),
                    Row(variable_key="Omlan202", show_in_chart=False),
                    Row(variable_key="Omlan203", show_in_chart=False),
                    Row(variable_key="Omlan204", show_in_chart=False),
                    Row(variable_key="Omlan205", show_in_chart=False),
                    Row(variable_key="Omlan206", show_in_chart=False),
                    Row(variable_key="Omlan207", show_in_chart=False),
                    Row(variable_key="Omlan208", show_in_chart=False),
                    Row(variable_key="Omlan209", show_in_chart=False),
                    Row(variable_key="Omlan210", show_in_chart=False),
                    Row(variable_key="Omlan211", show_in_chart=False),
                    Row(variable_key="Omlan212", show_in_chart=False),
                    Row(variable_key="Omlan213", show_in_chart=False),
                    Row(variable_key="Omlan299", is_sum=True),
                    Row(
                        description="Andel omlån av det totala antalet lån",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Omlan299", "Utlan399"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Utlån fysiskt bestånd",
                extra="Andel av total fysisk utlåning",
                rows=[
                    Row(
                        variable_key="Utlan301",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan301", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan302",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan302", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan303",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan303", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan304",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan304", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan305",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan305", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan306",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan306", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan307",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan307", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan308",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan308", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan309",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan309", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan310",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan310", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan311",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan311", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan312",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan312", "Utlan399"],
                    ),
                    Row(
                        variable_key="Utlan313",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan313", "Utlan399"],
                    ),
                    Row(variable_key="Utlan399", is_sum=True),
                    Row(
                        description="Antal fysiska utlån per kommuninvånare",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan399", "Population01"],
                    ),
                    Row(
                        description="Fysiska böcker med skriven text per invånare",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Utlan301", "Population01"],
                    ),
                ],
            ),
            Group(
                title="Läsning på plats i biblioteket",
                show_chart=False,
                rows=[
                    Row(variable_key="Laslan01"),
                    Row(variable_key="Laslan02"),
                    Row(variable_key="Laslan99"),
                    Row(
                        description="Beräkning lån på plats",
                        computation=(lambda a, b, c: ((a / b) / 2) / c),
                        variable_keys=["Laslan01", "Laslan02", "Open101"],
                    ),
                ],
            ),
            Group(
                title="Fjärrlån",
                rows=[
                    Row(description="Inom Sverige", label_only=True),
                    Row(variable_key="Fjarr101"),
                    Row(variable_key="Fjarr102"),
                    Row(description="Utanför Sverige", label_only=True),
                    Row(variable_key="Fjarr201"),
                    Row(variable_key="Fjarr202"),
                ],
            ),
            Group(
                title="Summering fjärrlån",
                show_chart=False,
                rows=[
                    Row(variable_key="Fjarr397"),
                    Row(variable_key="Fjarr398"),
                    Row(variable_key="Fjarr399", is_sum=True),
                    Row(
                        description="Andel utländska fjärrlån totalt",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Fjarr299", "Fjarr399"],
                        percentage=True,
                    ),
                    Row(
                        description="Nettofjärrinlåning in-ut",
                        computation=(lambda a, b: a - b),
                        variable_keys=["Fjarr397", "Fjarr398"],
                    ),
                ],
            ),
            Group(
                title="Användning av elektroniska samlingar",
                rows=[
                    Row(description="Antal sökningar", label_only=True),
                    Row(variable_key="Elan101"),
                    Row(variable_key="Elan102"),
                    Row(variable_key="Elan103"),
                    Row(variable_key="Elan104"),
                    Row(variable_key="Elan105"),
                    Row(variable_key="Elan106"),
                    Row(variable_key="Elan107"),
                    Row(variable_key="Elan108"),
                    Row(variable_key="Elan109"),
                    Row(variable_key="Elan199", is_sum=True),
                    Row(description="Antal nedladdningar", label_only=True),
                    Row(variable_key="Elan201"),
                    Row(variable_key="Elan202"),
                    Row(variable_key="Elan203"),
                    Row(variable_key="Elan204"),
                    Row(variable_key="Elan205"),
                    Row(variable_key="Elan206"),
                    Row(variable_key="Elan207"),
                    Row(variable_key="Elan208"),
                    Row(variable_key="Elan209"),
                    Row(variable_key="Elan299", is_sum=True),
                    Row(description="Antal nedladdade sektioner", label_only=True),
                    Row(variable_key="Elan301"),
                    Row(variable_key="Elan399", is_sum=True),
                    Row(
                        description="Total användning av de elektroniska samlingarna",
                        computation=(lambda a, b, c: a + b + c),
                        variable_keys=["Elan199", "Elan299", "Elan399"],
                    ),
                ],
            ),
            Group(
                title="Besök",
                rows=[
                    Row(variable_key="Besok01"),
                    Row(variable_key="Besok02"),
                    Row(variable_key="Besok03"),
                    Row(variable_key="Besok04"),
                    Row(variable_key="Besok05"),
                    Row(
                        description="Antal fysiska besök per invånare",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Besok01", "Population01"],
                    ),
                ],
            ),
            Group(
                title="Aktiva användare",
                rows=[
                    Row(variable_key="Aktiv01"),
                    Row(variable_key="Aktiv02"),
                    Row(variable_key="Aktiv04"),
                    Row(variable_key="Aktiv99", is_sum=True),
                    Row(variable_key="Aktiv03"),
                    Row(
                        description="Andel kvinnor som är aktiva låntagare",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Aktiv01", "Aktiv99"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel barn och unga som är aktiva låntagare",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Aktiv03", "Population03"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel aktiva användare per invånare",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Aktiv99", "Population01"],
                        percentage=True,
                    ),
                    Row(
                        description="Antal fysiska besök per antal aktiva användare",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Besok01", "Aktiv99"],
                    ),
                ],
            ),
            Group(
                title="Resurser",
                rows=[
                    Row(variable_key="Resurs01"),
                    Row(variable_key="Resurs02"),
                    Row(variable_key="Resurs03"),
                    Row(variable_key="Resurs04"),
                    Row(variable_key="Resurs05"),
                    Row(variable_key="Resurs06"),
                    Row(variable_key="Resurs07"),
                    Row(variable_key="Resurs08"),
                    Row(variable_key="Resurs09"),
                    Row(variable_key="Resurs10"),
                    Row(
                        description="Andel publika ytor",
                        computation=(lambda a, b: a / (a + b)),
                        variable_keys=["Resurs09", "Resurs10"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Öppettider",
                rows=[
                    Row(
                        description="Servicestället med de generösaste öppettiderna",
                        label_only=True,
                    ),
                    Row(variable_key="Open101"),
                    Row(variable_key="Open102"),
                    Row(variable_key="Open103"),
                    Row(variable_key="Open104"),
                    Row(variable_key="Open105"),
                    Row(variable_key="Open106"),
                    Row(
                        description="Övriga serviceställen sammantaget", label_only=True
                    ),
                    Row(variable_key="Open201"),
                    Row(variable_key="Open202"),
                    Row(variable_key="Open203"),
                    Row(variable_key="Open204"),
                    Row(variable_key="Open205"),
                    Row(variable_key="Open206"),
                    Row(
                        description="Medelantal öppetdagar per år",
                        computation=(lambda a, b, c: (a + b) / c),
                        variable_keys=["Open201", "Open101", "BemanService01"],
                    ),
                    Row(
                        description="Medelantal öppettimmar alla serviceställen",
                        computation=(lambda a, b, c: (a + b) / c),
                        variable_keys=["Open203", "Open103", "BemanService01"],
                    ),
                    Row(
                        description="Andel öppettimmar med reducerad service",
                        computation=(lambda a, b, c, d: (a + b) / (c + d)),
                        variable_keys=["Open104", "Open204", "Open103", "Open203"],
                        percentage=True,
                    ),
                    Row(
                        description="Andel öppettimmar utanför kontorstid",
                        computation=(lambda a, b, c, d: (a + b) / (c + d)),
                        variable_keys=["Open106", "Open206", "Open103", "Open203"],
                        percentage=True,
                    ),
                ],
            ),
            Group(
                title="Service",
                rows=[
                    Row(variable_key="Serv01"),
                    Row(variable_key="Serv02"),
                    Row(variable_key="Serv03"),
                    Row(variable_key="Serv04"),
                    Row(variable_key="Serv05"),
                    Row(variable_key="Serv06"),
                    Row(variable_key="Serv07"),
                ],
            ),
            Group(
                title="Publika aktivitetstillfällen",
                extra="Varav andel tillfällen för barn och unga",
                rows=[
                    Row(
                        variable_key="Publ101",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ201", "Publ101"],
                    ),
                    Row(
                        variable_key="Publ102",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ202", "Publ102"],
                    ),
                    Row(
                        variable_key="Publ103",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ203", "Publ103"],
                    ),
                    Row(
                        variable_key="Publ104",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ204", "Publ104"],
                    ),
                    Row(
                        variable_key="Publ105",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ205", "Publ105"],
                    ),
                    Row(
                        variable_key="Publ106",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ206", "Publ106"],
                    ),
                    Row(
                        variable_key="Publ107",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ207", "Publ107"],
                    ),
                    Row(
                        variable_key="Publ108",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ208", "Publ108"],
                    ),
                    Row(
                        variable_key="Publ109",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ209", "Publ109"],
                    ),
                    Row(
                        variable_key="Publ110",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ210", "Publ110"],
                    ),
                    Row(
                        variable_key="Publ111",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ211", "Publ111"],
                    ),
                    Row(
                        variable_key="Publ112",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ212", "Publ112"],
                    ),
                    Row(
                        variable_key="Publ113",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ213", "Publ113"],
                    ),
                    Row(
                        variable_key="Publ114",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ214", "Publ114"],
                    ),
                    Row(
                        variable_key="Publ115",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ215", "Publ115"],
                    ),
                    Row(
                        variable_key="Publ116",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ216", "Publ116"],
                    ),
                    Row(
                        variable_key="Publ117",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ217", "Publ117"],
                    ),
                    Row(
                        variable_key="Publ118",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ218", "Publ118"],
                    ),
                    Row(
                        variable_key="Publ119",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ219", "Publ119"],
                    ),
                    Row(
                        variable_key="Publ120",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ220", "Publ120"],
                    ),
                    Row(
                        variable_key="Publ199",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ299", "Publ199"],
                        is_sum=True,
                    ),
                    Row(
                        description="Andel publika aktiviteter primärt för barn/unga",
                        computation=(lambda a, b: a / b),
                        variable_keys=["Publ299", "Publ199"],
                        percentage=True,
                    ),
                    Row(description="", label_only=True),
                    Row(variable_key="Publ201", show_in_chart=False),
                    Row(variable_key="Publ202", show_in_chart=False),
                    Row(variable_key="Publ203", show_in_chart=False),
                    Row(variable_key="Publ204", show_in_chart=False),
                    Row(variable_key="Publ205", show_in_chart=False),
                    Row(variable_key="Publ206", show_in_chart=False),
                    Row(variable_key="Publ207", show_in_chart=False),
                    Row(variable_key="Publ208", show_in_chart=False),
                    Row(variable_key="Publ209", show_in_chart=False),
                    Row(variable_key="Publ210", show_in_chart=False),
                    Row(variable_key="Publ211", show_in_chart=False),
                    Row(variable_key="Publ212", show_in_chart=False),
                    Row(variable_key="Publ213", show_in_chart=False),
                    Row(variable_key="Publ214", show_in_chart=False),
                    Row(variable_key="Publ215", show_in_chart=False),
                    Row(variable_key="Publ216", show_in_chart=False),
                    Row(variable_key="Publ217", show_in_chart=False),
                    Row(variable_key="Publ218", show_in_chart=False),
                    Row(variable_key="Publ219", show_in_chart=False),
                    Row(variable_key="Publ220", show_in_chart=False),
                    Row(variable_key="Publ299", is_sum=True, show_in_chart=False),
                ],
            ),
        ]
    )

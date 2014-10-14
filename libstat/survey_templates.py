# -*- coding: utf-8 -*-
from libstat.models import Section, Group, Cell, Row, SurveyTemplate

survey_template = SurveyTemplate(
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
                    description="",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="1. Vad heter du som fyller i enkäten?",
                            explanation="Kontaktuppgift, om vi har någon fråga om lämnade uppgifter.",
                            cells=[Cell(variable_key=u"Namn01", types=["text"])]
                        ),
                        Row(
                            description="2. Vad har du för e-postadress?",
                            explanation="Vi skickar länk till rapporten när den publiceras. E-postadressen valideras automatiskt så att du fyllt i en användbar e-postadress, det går därför inte att skriva två adresser i fältet.",
                            cells=[Cell(variable_key=u"Epost01", types=['email', 'required'])]
                        ),
                        Row(
                            description="3. Vänligen fyll i ditt telefonnummer, inklusive riktnummer.",
                            explanation="Används så att vi kan kontakta dig om vi har några frågor om de lämnade uppgifterna",
                            cells=[Cell(variable_key=u"Tele01", types=["text"])]
                        ),
                        Row(
                            description="4. Vänligen skriv in länk till en webbplats där vi kan nå den biblioteksplan eller annan plan som styr er verksamhet.",
                            explanation="",
                            cells=[Cell(variable_key=u"Plan01", types=["text"])]
                        )
                    ]
                ),
                # TODO Välja bibliotek (5)
                Group(
                    description="",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="6. Enkätens uppgifter avser totalt antal bemannade servicesställen:",
                            explanation="",
                            cells=[Cell(variable_key=u"BemanService01", types=['required', 'integer'])]
                        ),
                        Row(
                            description="7. Hur många av de bemannade serviceställena är integrerade bibliotek? Folk- och skolbibliotek alternativt forsknings- och sjukhusbibliotek alternativt folk- och forskningsbibliotek?",
                            explanation="",
                            cells=[Cell(variable_key=u"Integrerad01", types=['required', 'integer'])]
                        )
                    ]
                ),
                Group(
                    description="8. Till de bemannade servicesställen som den här enkäten avser är det kanske också kopplat ett antal obemannade utlåningsställen där vidare låneregistrering inte sker. Antal obemannade utlåningsställen och utlån till sådana:",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Antal obemannade utlåningsställen där vidare låneregistrering inte sker",
                            explanation="",
                            cells=[Cell(variable_key=u"Obeman01", types=['required', 'integer'])]
                        ),
                        Row(
                            description="Antal utlån till servicesställen/institutioner där vidare lånregistrering inte sker under kalenderåret (inkl. institutionslån och depositioner)",
                            explanation="",
                            cells=[Cell(variable_key=u"ObemanLan01", types=['required', 'integer'])]
                        )
                    ]
                ),
                Group(
                    description="9. Hur många bokbussar, bokbilar och bokbusshållplatser administrerar de uppräknade biblioteksenheterna? Om ni köper tjänsten av ett annat bibliotek som sköter administrationen uppge värdet 0 för att omöjliggöra dubbelräkning på riksnivå. Ange 0 om frågan inte är aktuell för er.",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Antal bokbussar",
                            explanation="",
                            cells=[Cell(variable_key=u"Bokbuss01", types=['required', 'integer'])]
                        ),
                        Row(
                            description="Antal bokbusshållplatser inom kommunen",
                            explanation="",
                            cells=[Cell(variable_key=u"BokbussHP01", types=['required', 'integer'])]
                        ),
                        Row(
                            description="Antal bokbilar, transportfordon",
                            explanation="",
                            cells=[Cell(variable_key=u"Bokbil01", types=['integer'])]
                        )
                    ]
                ),
                Group(
                    description="10. Antal personer som biblioteket förväntas betjäna. Exempelvis antal elever (skolbibliotek), antal anställda (myndighetsbibliotek), antal helårsekvivalenter (forskningsbibliotek). Uppgift om antal kommuninnevånare behöver inte lämnas av folkbibliotek.",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Antal personer",
                            explanation="",
                            cells=[Cell(variable_key=u"Population01", types=['integer'])]
                        )
                    ]
                ),
                ]
        ),
        Section(
            title=u"Frågor om bemanning och personal",  # Personkomm variabel för comment
            comment=u"Här kan du lämna eventuella kommentarer till frågeområdet personal. Vänligen skriv inga siffror här.",
            groups=[
                Group(
                    description="11. Hur många årsverken avsattes för biblioteksverksamheten under kalenderåret?",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Antal årsverken bibliotekarier och dokumentalister",
                            explanation="",
                            cells=[Cell(variable_key=u"Arsverke01", types=['sum', 'numeric'], sum_siblings=["Arsverke02","Arsverke03","Arsverke04"])]
                        ),
                        Row(
                            description="Antal årsverken biblioteksassistenter och lärarbibliotekarier",
                            explanation="",
                            cells=[Cell(variable_key=u"Arsverke02", types=['sum', 'numeric'], sum_siblings=["Arsverke01","Arsverke03","Arsverke04"])]
                        ),
                        Row(
                            description="Antal årsverken specialister inom IT, information eller ämnessakkunniga, fackkunniga",
                            explanation="",
                            cells=[Cell(variable_key=u"Arsverke03", types=['sum', 'numeric'], sum_siblings=["Arsverke01","Arsverke02","Arsverke04"])]
                        ),
                        Row(
                            description="Antal årsverken övrig personal inklusive kvällspersonal studentvakter, chaufförer, vaktmästare",
                            explanation="",
                            cells=[Cell(variable_key=u"Arsverke04", types=['sum', 'numeric'], sum_siblings=["Arsverke01","Arsverke02","Arsverke03"])]
                        ),
                        Row(
                            description="Totalt antal årsverken avsatt bemanning för biblioteksverksamhet",
                            explanation="",
                            cells=[Cell(variable_key=u"Arsverke99", types=['sum', 'numeric'], sum_of=["Arsverke01","Arsverke02","Arsverke03","Arsverke04"])]
                        ),
                        Row(
                            description="- varav antal av dessa ovanstående årsverken var särskilt avsatta för barn och unga",
                            explanation="",
                            cells=[Cell(variable_key=u"Arsverke05", types=['required', 'numeric'])]
                        )
                    ]
                ),
                Group(
                    description="12. Hur många personer arbetade inom biblioteksverksamheten 31 mars?",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Antal anställda kvinnor",
                            explanation="",
                            cells=[Cell(variable_key=u"Personer01", types=['sum', 'integer'], sum_siblings=['Personer02'])]
                        ),
                        Row(
                            description="Antal anställda män",
                            explanation="",
                            cells=[Cell(variable_key=u"Personer02", types=['sum', 'integer'], sum_siblings=['Personer01'])]
                        ),
                        Row(
                            description="Totalt antal anställda personer",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Personer99", types=['sum', 'integer'], sum_of=[u"Personer01", u"Personer02"])]
                        )
                    ]
                )
            ]
        ),
        Section(
            title=u"Frågor om ekonomi",  # TODO Koppla comment till Ekonomikomm
            comment=u"Här kan du lämna eventuella kommentarer till frågeområdet ekonomi. Vänligen skriv inga siffror här.",
            groups=[
                Group(
                    description="13. Vilka utgifter hade biblioteksverksamheten under kalenderåret? Antal hela kronor inklusive mervärdesskatt. Avrunda inte till tusental. Vänligen skriv uppgifterna utan punkt, mellanslag eller kommatecken.",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Inköp av tryckta medier och audiovisuella medier",
                            explanation="",
                            cells=[Cell(variable_key=u"Utgift01", types=['sum','integer'],
                                        sum_siblings=[u"Utgift02", u"Utgift03", u"Utgift04", u"Utgift05", u"Utgift06"])]
                        ),
                        Row(
                            description="Inköp av virtuella e-baserade media och databaslicenser (exklusive kostnader för biblioteksdatasystemet)",
                            explanation="",
                            cells=[Cell(variable_key=u"Utgift02", types=['sum','integer'],
                                        sum_siblings=[u"Utgift01", u"Utgift03", u"Utgift04", u"Utgift05", u"Utgift06"])]
                        ),
                        Row(
                            description="Lönekostnader personal",
                            explanation="",
                            cells=[Cell(variable_key=u"Utgift03", types=['sum','integer'],
                                        sum_siblings=[u"Utgift01", u"Utgift02", u"Utgift04", u"Utgift05", u"Utgift06"])]
                        ),
                        Row(
                            description="Kostnader för personalens kompetensutveckling",
                            explanation="",
                            cells=[Cell(variable_key=u"Utgift04", types=['sum','integer'],
                                        sum_siblings=[u"Utgift01", u"Utgift02", u"Utgift03", u"Utgift05", u"Utgift06"])]
                        ),
                        Row(
                            description="Lokalkostnader",
                            explanation="",
                            cells=[Cell(variable_key=u"Utgift05", types=['sum','integer'],
                                        sum_siblings=[u"Utgift01", u"Utgift02", u"Utgift03", u"Utgift04", u"Utgift06"])]
                        ),
                        Row(
                            description="Övriga driftskostnader som inte ingår i punkterna ovan (inklusive kostnader för bibliotekssystemet)",
                            explanation="",
                            cells=[Cell(variable_key=u"Utgift06", types=['sum','integer'],
                                        sum_siblings=[u"Utgift01", u"Utgift02", u"Utgift03", u"Utgift04", u"Utgift05"])]
                        ),
                        Row(
                            description="Totala driftskostnader för biblioteksverksamheten (summan av ovanstående)",
                            explanation="",
                            cells=[Cell(variable_key=u"Utgift99", types=['sum','integer'],
                                        sum_of=[u"Utgift01", u"Utgift02", u"Utgift03", u"Utgift04", u"Utgift05",
                                                u"Utgift06"])]
                        ),
                        Row(
                            description="Investeringsutgifter, inklusive kapitalkostnader för dessa",
                            explanation="",
                            cells=[Cell(variable_key=u"Utgift07", types=['integer'])]
                        )
                    ]
                ),
                Group(
                    description="14. Vilka egengenererade intäkter hade biblioteksverksamheten? Antal hela kronor. Avrunda inte till tusental.",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Projektmedel som inte kommer från huvudmannen eller moderorganisationen samt sponsring och gåvor",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Intakt01", types=['sum','integer'], sum_siblings=[u"Intakt02", u"Intakt03"])]
                        ),
                        Row(
                            description="Försäljning av bibliotekstjänster och personalresurser till andra huvudmän, organisationer och företag",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Intakt02", types=['sum','integer'], sum_siblings=[u"Intakt01", u"Intakt03"])]
                        ),
                        Row(
                            description="Försenings- och reservationsutgifter eller intäkter av uthyrningsverksamhet samt försäljning av böcker och profilprodukter",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Intakt03", types=['sum','integer'], sum_siblings=[u"Intakt01", u"Intakt02"])]
                        ),
                        Row(
                            description="Totalt antal kronor egengenererade inkomster",
                            explanation="",
                            cells=[Cell(variable_key=u"Intakt99", types=['sum','integer'],
                                        sum_of=[u"Intakt01", u"Intakt02", u"Intakt03"])]
                        ),
                        ]
                )
            ]
        ),
        Section(
            title=u"Bestånd – nyförvärv",
            comment=u"",
            groups=[
                Group(
                    description="15. Hur stort var det fysiska mediebeståndet och det elektroniska titelbeståndet 31 december och hur många fysiska nyförvärv gjordes under kalenderåret uppdelat på olika medietyper? Om ni bara kan få fram fysiskt bestånd genom att räkna hyllmeter, använd omräkningstal 40 medier per hyllmeter om ni beräknar antal utifrån uppgift om hyllmeter.",
                    columns=3,
                    headers=[],
                    rows=[]
                )
            ]
        ),
        ]
)
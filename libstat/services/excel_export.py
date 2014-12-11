# -*- coding: utf-8 -*-
from openpyxl import Workbook
from data.principals import principal_for_library_type
from libstat.models import Survey


def surveys_to_excel_workbook(survey_ids):
    surveys = Survey.objects.filter(id__in=survey_ids).order_by('library__name')

    headers = [
        "Bibliotek",
        "Sigel",
        "Bibliotekstyp",
        "Status",
        "Email",
        "Kommunkod",
        "Stad",
        "Adress",
        "Huvudman",
        "Kan publiceras?"
    ]
    headers += [unicode(observation.variable.key) for observation in surveys[0].observations]

    workbook = Workbook(encoding="utf-8")
    worksheet = workbook.active
    worksheet.append(headers)

    for survey in surveys:
        row = [
            survey.library.name,
            survey.library.sigel,
            survey.library.library_type,
            Survey.status_label(survey.status),
            survey.library.email,
            survey.library.municipality_code,
            survey.library.city,
            survey.library.address,
            principal_for_library_type[survey.library.library_type]
            if survey.library.library_type in principal_for_library_type else None,
            "Ja" if survey.can_publish() else "Nej: " + survey.reasons_for_not_able_to_publish()
        ]
        for observation in survey.observations:
            row.append(observation.value)
        worksheet.append(row)

    return workbook
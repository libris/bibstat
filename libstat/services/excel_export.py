# -*- coding: utf-8 -*-
import glob
import os
import datetime
from django.core.files import File

from openpyxl import Workbook, load_workbook
from openpyxl.writer.excel import save_virtual_workbook

from data.principals import principal_for_library_type
from libstat.models import Survey, OpenData, Variable


DATE_FORMAT = "%Y_%m_%d_%H_%M_%S"


def _cache_path(year, date_str=None):
    return "data/public_exports/public_export_{} {}.xslx".format(year, date_str if date_str else "*")


def _cached_workbook_exists_and_is_valid(year):
    paths = sorted(glob.glob("{}/{}".format(os.getcwd(), _cache_path(year))))
    if not paths:
        return False

    cache_date = datetime.datetime.strptime(paths[-1].split(" ")[-1].split(".")[0], DATE_FORMAT)
    latest_publication = OpenData.objects.first().date_modified

    return cache_date > latest_publication


def _cache_workbook(workbook, year):
    with open(_cache_path(year, datetime.datetime.utcnow().strftime(DATE_FORMAT)), "w") as f:
        File(f).write(save_virtual_workbook(workbook))


def public_excel_workbook(year):
    if not _cached_workbook_exists_and_is_valid(year):
        _cache_workbook(_published_open_data_as_workbook(year), year)
    return sorted(glob.glob(_cache_path(year)))[-1]


def _published_open_data_as_workbook(year):
    workbook = Workbook(encoding="utf-8")
    worksheet = workbook.active
    worksheet.title = u"Värden"

    variable_keys = list(OpenData.objects.filter(is_active=True, sample_year=year).distinct("variable_key"))
    sigels = list(OpenData.objects.filter(is_active=True, sample_year=year).distinct("sigel"))

    libraries = {}
    for sigel in sigels:
        libraries[sigel] = dict.fromkeys(variable_keys)

    for open_data in OpenData.objects.filter(is_active=True, sample_year=year).only("library_name", "variable_key",
                                                                                    "sigel", "value"):
        libraries[open_data.sigel][open_data.variable_key] = open_data.value

    header = ["Bibliotek", "Sigel", "Bibliotekstyp", "Kommunkod", "Stad", "Adress"]
    variable_index = {}
    for index, key in enumerate(variable_keys):
        variable_index[key] = index + 6
        header.append(key)
    worksheet.append(header)

    for sigel in libraries:
        library = Survey.objects.get(library__sigel=sigel).library
        row = [""] * len(header)
        row[0] = library.name
        row[1] = sigel if year >= 2014 else ""  # Do not show auto-generated sigels (used before 2014)
        row[2] = library.library_type
        row[3] = library.municipality_code
        row[4] = library.city
        row[5] = library.address

        for key in variable_keys:
            row[variable_index[key]] = libraries[sigel][key]
        worksheet.append(row)

    variable_sheet = workbook.create_sheet()
    variable_sheet.title = u"Definitioner"
    for variable in Variable.objects.filter(key__in=variable_keys):
        variable_sheet.append([variable.key, variable.description])

    return workbook


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
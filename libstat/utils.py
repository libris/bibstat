# -*- coding: UTF-8 -*-
import datetime

ALL_TARGET_GROUPS_label = "Samtliga bibliotek"
SURVEY_TARGET_GROUPS = (
    ('natbib', 'Nationalbibliotek'),
    ('folkbib', 'Folkbibliotek'),
    ('folkskolbib', 'Folk- och skolbibliotek'),
    ('specbib', 'Specialbibliotek'),
    ('sjukbib', 'Sjukhusbibliotek'),
    ('myndbib', 'Myndighetsbibliotek'),
    ('busbib', 'Företagsbibliotek'),
    ('musbib', 'Arkiv / museibibliotek'),
    ('muskom', 'Kommunalt museibibliotek'),
    ('muslan', 'Länsmuseibibliotek'),
    ('musstat', 'Statligt museibibliotek'),
    ('skolbib', 'Skolbibliotek'),
    ('friskol', 'Friskolebibliotek'),
    ('gymbib', 'Gymnasiebibliotek'),
    ('frisgym', 'Friskolegymnasiebibliotek'),
    ('statskol', 'Statligt skolbibliotek'),
    ('vuxbib', 'Bibliotek på komvux / lärcentra'),
    ('univbib', 'Universitets / högskolebibliotek'),
    ('folkhogbib', 'Folkhögskolebibliotek'),
    ('ovrbib', 'Övriga'),
)
targetGroups = dict(SURVEY_TARGET_GROUPS)

TYPE_STRING = ("string", "Text")
TYPE_BOOLEAN = ("boolean", "Boolesk")
TYPE_INTEGER = ("integer", "Integer")
TYPE_LONG = ("long", "Long")
TYPE_DECIMAL = ("decimal", "Decimal")
TYPE_PERCENT = ("percent", "Procent")
TYPE_PHONE = ("phonenumber", "Telefonnummer")
TYPE_TEXTAREA = ("textarea", "Textruta")
TYPE_EMAIL = ("email", "E-post")

VARIABLE_TYPES = (TYPE_STRING, TYPE_BOOLEAN, TYPE_INTEGER, TYPE_LONG, TYPE_DECIMAL, TYPE_PERCENT, TYPE_PHONE, TYPE_TEXTAREA, TYPE_EMAIL)

variableTypes = dict(VARIABLE_TYPES)

rdfVariableTypes = {TYPE_STRING[0]: "xsd:string", TYPE_BOOLEAN[0]: "xsd:boolean", TYPE_INTEGER[0]: "xsd:integer",
                    TYPE_LONG[0]: "xsd:long", TYPE_DECIMAL[0]: "xsd:decimal", TYPE_PERCENT[0]: "xsd:decimal"}

DATA_IMPORT_nonMeasurementCategories = ["Bakgrundsvariabel", "Tid", "Befolkning", "Bakgrundsvariabler"]

ISO8601_utc_format = "%Y-%m-%dT%H:%M:%S.%fZ"


def parse_datetime_from_isodate_str(date_str):
    # Note: Timezone designator not supported ("+01:00").
    if not date_str:
        return None

    datetime_obj = parse_datetime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
    if not datetime_obj:
        datetime_obj = parse_datetime(date_str, "%Y-%m-%dT%H:%M:%S")
    if not datetime_obj:
        datetime_obj = parse_datetime(date_str, "%Y-%m-%dT%H:%M")
    if not datetime_obj:
        datetime_obj = parse_datetime(date_str, "%Y-%m-%dT%H")
    if not datetime_obj:
        datetime_obj = parse_datetime(date_str, "%Y-%m-%d")
    if not datetime_obj:
        datetime_obj = parse_datetime(date_str, "%Y-%m")
    if not datetime_obj:
        datetime_obj = parse_datetime(date_str, "%Y")
    return datetime_obj


def parse_datetime(date_str, date_format):
    try:
        return datetime.datetime.strptime(date_str, date_format)
    except ValueError:
        return None

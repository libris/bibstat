# -*- coding: UTF-8 -*-
import datetime

ALL_TARGET_GROUPS_label = "Samtliga bibliotek"
SURVEY_TARGET_GROUPS = (
    (u'natbib', u'Nationalbibliotek'),
    (u'folkbib', u'Folkbibliotek'),
    (u'folkskolbib', u'Folk- och skolbibliotek'),
    (u'specbib', u'Specialbibliotek'),
    (u'sjukbib', u'Sjukhusbibliotek'),
    (u'myndbib', u'Myndighetsbibliotek'),
    (u'busbib', u'Företagsbibliotek'),
    (u'musbib', u'Arkiv / museibibliotek'),
    (u'muskom', u'Kommunalt museibibliotek'),
    (u'muslan', u'Länsmuseibibliotek'),
    (u'musstat', u'Statligt museibibliotek'),
    (u'skolbib', u'Skolbibliotek'),
    (u'friskol', u'Friskolebibliotek'),
    (u'gymbib', u'Gymnasiebibliotek'),
    (u'frisgym', u'Friskolegymnasiebibliotek'),
    (u'statskol', u'Statligt skolbibliotek'),
    (u'vuxbib', u'Bibliotek på komvux / lärcentra'),
    (u'univbib', u'Universitets / högskolebibliotek'),
    (u'folkhogbib', u'Folkhögskolebibliotek'),
    (u'ovrbib', u'Övriga'),
)
targetGroups = dict(SURVEY_TARGET_GROUPS)

TYPE_STRING = (u"string", u"Text")
TYPE_BOOLEAN = (u"boolean", u"Boolesk")
TYPE_INTEGER = (u"integer", u"Integer")
TYPE_LONG = (u"long", u"Long")
TYPE_DECIMAL = (u"decimal", u"Decimal")
TYPE_PERCENT = (u"percent", u"Procent")
TYPE_PHONE = (u"phonenumber", u"Telefonnummer")
TYPE_TEXTAREA = (u"textarea", u"Textruta")
TYPE_EMAIL = (u"email", u"E-post")

VARIABLE_TYPES = (TYPE_STRING, TYPE_BOOLEAN, TYPE_INTEGER, TYPE_LONG, TYPE_DECIMAL, TYPE_PERCENT, TYPE_PHONE, TYPE_TEXTAREA, TYPE_EMAIL)

variableTypes = dict(VARIABLE_TYPES)

rdfVariableTypes = {TYPE_STRING[0]: u"xsd:string", TYPE_BOOLEAN[0]: u"xsd:boolean", TYPE_INTEGER[0]: u"xsd:integer",
                    TYPE_LONG[0]: u"xsd:long", TYPE_DECIMAL[0]: u"xsd:decimal", TYPE_PERCENT[0]: u"xsd:decimal"}

DATA_IMPORT_nonMeasurementCategories = [u"Bakgrundsvariabel", u"Tid", u"Befolkning", u"Bakgrundsvariabler"]

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

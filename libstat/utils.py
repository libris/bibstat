# -*- coding: UTF-8 -*-
import datetime

"""
    Target groups for variables and surveys
"""
ALL_TARGET_GROUPS_label = u"Samtliga bibliotekstyper"
PUBLIC_LIBRARY = ("public", "Folkbibliotek")
RESEARCH_LIBRARY = ("research", "Forskningsbibliotek")
HOSPITAL_LIBRARY = ("hospital", "Sjukhusbibliotek")
SCHOOL_LIBRARY = ("school", "Skolbibliotek")
SURVEY_TARGET_GROUPS = (PUBLIC_LIBRARY, RESEARCH_LIBRARY, HOSPITAL_LIBRARY, SCHOOL_LIBRARY)
targetGroups = dict(SURVEY_TARGET_GROUPS)


"""
    Status of survey responses
"""
NOT_VIEWED = (u"not_viewed", u"Ej öppnad")
INITIATED = (u"initiated", u"Påbörjad")
SUBMITTED = (u"submitted", u"Inskickad")
CONTROLLED = (u"controlled", u"Kontrollerad")
PUBLISHED = (u"published", u"Publicerad")
SURVEY_RESPONSE_STATUSES = (NOT_VIEWED, INITIATED, SUBMITTED, CONTROLLED, PUBLISHED)
survey_response_statuses = dict(SURVEY_RESPONSE_STATUSES)

"""
    Types for variables
"""
TYPE_STRING = (u"string", u"Text")
TYPE_BOOLEAN = (u"boolean", u"Boolesk")
TYPE_INTEGER = (u"integer", u"Integer")
TYPE_LONG = (u"long", u"Long")
TYPE_DECIMAL = (u"decimal", u"Decimal")
TYPE_PERCENT = (u"percent", u"Procent")
# TODO: TYPE_DECIMAL1 = (u"decimal1", u"1 decimals noggrannhet"), Type_DECIMAL2 = (u"decimal2", u"2 decimalers noggrannhet") isf TYPE_DECIMAL
#TODO: TYPE_TEXT = (u"text", u"Text") för kommentarer (textarea), TYPE_STRING=(u"string", u"Textsträng") för icke-numeriska värden "numerical" (input)
VARIABLE_TYPES = (TYPE_STRING, TYPE_BOOLEAN, TYPE_INTEGER, TYPE_LONG, TYPE_DECIMAL, TYPE_PERCENT)


"""
    Mapping between stored variable type and RDF compatible type to be presented as open data
"""
rdfVariableTypes = {TYPE_STRING[0]: u"xsd:string", TYPE_BOOLEAN[0]: u"xsd:boolean", TYPE_INTEGER[0]: u"xsd:integer",
                    TYPE_LONG[0]: u"xsd:long", TYPE_DECIMAL[0]: u"xsd:decimal", TYPE_PERCENT[0]: u"xsd:decimal"}


"""
    Useful definitions when importing data from spreadsheets
"""
DATA_IMPORT_nonMeasurementCategories = [u"Bakgrundsvariabel", u"Tid", u"Befolkning", u"Bakgrundsvariabler"]


"""
    Datetime in ISO8601 format with apppending 'Z' to indicate UTC time zone
"""
ISO8601_utc_format = "%Y-%m-%dT%H:%M:%S.%fZ"


def parse_datetime_from_isodate_str(date_str):
    """
        Parse a datetime from an ISO8601 formatted date string. 
        Note: Timezone designator not supported ("+01:00").
    """
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
    """
        Parse a datetime string with specified format to a datetime object
    """
    try:
        return datetime.datetime.strptime(date_str, date_format)
    except ValueError:
        return None


def target_groups_label(value):
    """
        Get a string label for a list or a single target group key.
    """
    display_names = []
    if value:
        if isinstance(value, list):
            if set(value) == set(targetGroups.keys()):
                display_names.append(ALL_TARGET_GROUPS_label)
            else:
                for tg in value:
                    if tg in targetGroups:
                        display_names.append(targetGroups[tg])
        else:
            if value in targetGroups:
                display_names.append(targetGroups[value])
    return ", ".join(display_names)
        

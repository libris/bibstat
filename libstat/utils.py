import datetime

from python_ipware import IpWare

ALL_TARGET_GROUPS_label = "Samtliga bibliotek"
SURVEY_TARGET_GROUPS = (
    ("natbib", "Nationalbibliotek"),
    ("folkbib", "Folkbibliotek"),
    ("folkskolbib", "Folk- och skolbibliotek"),
    ("specbib", "Specialbibliotek"),
    ("sjukbib", "Sjukhusbibliotek"),
    ("myndbib", "Myndighetsbibliotek"),
    ("busbib", "Företagsbibliotek"),
    ("musbib", "Arkiv / museibibliotek"),
    ("muskom", "Kommunalt museibibliotek"),
    ("muslan", "Länsmuseibibliotek"),
    ("musstat", "Statligt museibibliotek"),
    ("skolbib", "Skolbibliotek"),
    ("friskol", "Friskolebibliotek"),
    ("gymbib", "Gymnasiebibliotek"),
    ("frisgym", "Friskolegymnasiebibliotek"),
    ("statskol", "Statligt skolbibliotek"),
    ("vuxbib", "Bibliotek på komvux / lärcentra"),
    ("univbib", "Universitets / högskolebibliotek"),
    ("folkhogbib", "Folkhögskolebibliotek"),
    ("ovrbib", "Övriga"),
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

VARIABLE_TYPES = (
    TYPE_STRING,
    TYPE_BOOLEAN,
    TYPE_INTEGER,
    TYPE_LONG,
    TYPE_DECIMAL,
    TYPE_PERCENT,
    TYPE_PHONE,
    TYPE_TEXTAREA,
    TYPE_EMAIL,
)

variableTypes = dict(VARIABLE_TYPES)

rdfVariableTypes = {
    TYPE_STRING[0]: "xsd:string",
    TYPE_BOOLEAN[0]: "xsd:boolean",
    TYPE_INTEGER[0]: "xsd:integer",
    TYPE_LONG[0]: "xsd:long",
    TYPE_DECIMAL[0]: "xsd:decimal",
    TYPE_PERCENT[0]: "xsd:decimal",
}

DATA_IMPORT_nonMeasurementCategories = [
    "Bakgrundsvariabel",
    "Tid",
    "Befolkning",
    "Bakgrundsvariabler",
]

ISO8601_utc_format = "%Y-%m-%dT%H:%M:%S.%fZ"

ipw = IpWare()


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


def get_ip_for_logging(request):
    # We use ipware (ipw) tp easily get the "real" client IP.
    # Might need some adjustments depending on the environment, e.g. specifying
    # trusted proxies.
    # This is *ONLY* for logging purposes.
    ip, trusted_route = ipw.get_client_ip(request.META)
    return ip


def get_log_prefix(request, survey_id=None, survey_title=None):
    log_prefix = f"[IP: {get_ip_for_logging(request)}]"
    if request.user.is_superuser:
        log_prefix = f"{log_prefix} [ADMIN]"
    if survey_id:
        log_prefix = f"{log_prefix} [survey: {survey_id}]"
    if survey_title:
        log_prefix = f"{log_prefix} [{survey_title}]"
    return log_prefix

# -*- coding: utf-8 -*-
import requests
from bibstat import settings
from libstat.models import Library, ExternalIdentifier
from libstat.utils import SURVEY_TARGET_GROUPS

def check_library_criteria(json_data):
    if not json_data.get("country_code", None) == "se":
        return False

    if not json_data.get("statistics", None):
        return False

    if json_data.get("library_type", None) not in [g[0] for g in SURVEY_TARGET_GROUPS]:
        return False

    if json_data.get("library_type", None) == "busbib":
        return False

    if not json_data.get("municipality_code", None):
        return False

    return True


def library_from_json(json_data):
    library = Library()
    library.sigel = json_data.get("sigel", None)
    library.name = json_data.get("name", None)
    if library.name:
        library.name = library.name.strip()
    library.municipality_code = json_data.get("municipality_code", None)
    library.library_type = json_data.get("library_type", None)
    location = next((a for a in json_data["address"] if a["address_type"] == "stat"), None)
    library.address = location["street"] if location and location["street"] else None
    library.city = location["city"] if location and location["city"] else None
    library.zip_code = location["zip_code"] if location and location["zip_code"] else None
    contacts = json_data.get("contact", None)
    if contacts:
        library.email = next((c["email"] for c in contacts
                            if "email" in c and c["contact_type"] == "statans"), None)
    school_code = json_data.get("school_code", None)
    if school_code:
        external_identifier = ExternalIdentifier(type="school_code", identifier=school_code)
        library.external_identifiers = [external_identifier]

    return library


def fetch_libraries():
    libraries = []
    # bibdb api pages by 200, let 30 000 be upper limit in case api is broken
    for start_index in range(0, 30000, 200):
        response = requests.get(
            url="%s/api/lib?dump=true&start=%d" % (settings.BIBDB_BASE_URL, start_index),
            headers={"APIKEY-AUTH-HEADER": "bibstataccess"}) # KP 180110

        if not response.json().get("libraries", None):
            break

        for json_data in response.json()["libraries"]:
            if check_library_criteria(json_data):
                library = library_from_json(json_data)
                if library:
                    libraries.append(library)

    return libraries

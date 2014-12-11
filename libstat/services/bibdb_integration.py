# -*- coding: utf-8 -*-
import requests
from libstat.models import Library
from libstat.utils import SURVEY_TARGET_GROUPS


def library_from_json(json_data):
    if not json_data["country_code"] == "se":
        return None

    if json_data.get("library_type", None) not in [g[0] for g in SURVEY_TARGET_GROUPS]:
        return None

    if json_data.get("library_type", None) == "busbib":
        return None

    library = Library()
    library.sigel = json_data.get("sigel", None)
    library.name = json_data.get("name", None)
    if library.name:
        library.name = library.name.strip()
    library.municipality_code = json_data.get("municipality_code", None)
    library.library_type = json_data.get("library_type", None)
    location = next((a for a in json_data["address"] if a["address_type"] == "gen"), None)
    library.address = location["street"] if location and location["street"] else None
    library.city = location["city"] if location and location["city"] else None
    library.email = next((c["email"] for c in json_data["contact"]
                          if "email" in c and c["contact_type"] == "statans"), None)

    return library


def fetch_libraries():
    libraries = []
    # bibdb api paginated by 200 and had ca. 2800 responses when this was written
    for start_index in range(0, 6000, 200):
        response = requests.get(
            url="http://bibdb.libris.kb.se/api/lib?dump=true&start=%d" % start_index,
            headers={"APIKEY_AUTH_HEADER": "bibstataccess"})

        for json_data in response.json()["libraries"]:
            library = library_from_json(json_data)
            if library:
                libraries.append(library)
    return libraries
# -*- coding: utf-8 -*-
from libstat.services.bibdb_integration import library_from_json
from libstat.tests import MongoTestCase


class TestBibdbIntegration(MongoTestCase):
    def setUp(self):
        self._dummy_json_data = {
            "country_code": "se",
            "sigel": "lib1_sigel",
            "name": "lib1",
            "library_type": "sjukbib",
            "municipality_code": "1793",
            "address":
                [
                    {
                        "address_type": "gen",
                        "city": "lib1_city",
                        "street": "street1"
                    },
                    {
                        "address_type": "ill",
                        "city": "ill_lib1_city",
                        "street": "ill_street1"
                    }
                ],
            "contact":
                [
                    {
                        "contact_type": "orgchef",
                        "email": "dont@care.atall"
                    },
                    {
                        "contact_type": "statans",
                        "email": "lib1@dom.top"
                    }
                ]
        }

    def test_creates_library_from_dict(self):
        json_data = self._dummy_json_data

        library = library_from_json(json_data)

        self.assertEquals(library.sigel, "lib1_sigel")
        self.assertEquals(library.name, "lib1")
        self.assertEquals(library.city, "lib1_city")
        self.assertEquals(library.address, "street1")
        self.assertEquals(library.email, "lib1@dom.top")
        self.assertEquals(library.municipality_code, "1793")
        self.assertEquals(library.library_type, "sjukbib")

    def test_does_not_import_non_swedish_libraries(self):
        json_data = self._dummy_json_data
        json_data["country_code"] = "dk"

        library = library_from_json(json_data)

        self.assertEquals(library, None)

    def test_does_not_import_busbib(self):
        json_data = self._dummy_json_data
        json_data["library_type"] = "busbib"

        library = library_from_json(json_data)

        self.assertEquals(library, None)

    def test_does_not_import_library_with_invalid_library_type(self):
        json_data = self._dummy_json_data
        json_data["library_type"] = "does_not_exist"

        library = library_from_json(json_data)

        self.assertEquals(library, None)

    def test_trims_blank_spaces_from_library_name(self):
        json_data = self._dummy_json_data
        json_data["name"] = "  a b c  "

        library = library_from_json(json_data)

        self.assertEquals(library.name, "a b c")

    def test_does_not_library_import_if_no_municipality_code(self):
        json_data = self._dummy_json_data
        json_data.pop("municipality_code")

        library = library_from_json(json_data)

        self.assertEquals(library, None)
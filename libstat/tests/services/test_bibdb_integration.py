# -*- coding: utf-8 -*-
from libstat.services.bibdb_integration import check_library_criteria, library_from_json
from libstat.tests import MongoTestCase


class TestBibdbIntegration(MongoTestCase):
    def setUp(self):
        self._dummy_json_data = {
            "country_code": "se",
            "sigel": "lib1_sigel",
            "statistics": "true",
            "name": "lib1",
            "library_type": "sjukbib",
            "municipality_code": "1793",
            "school_code": "12345678",
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
                    },
                    {
                        "address_type": "stat",
                        "city": "stat_lib1_city",
                        "street": "stat_street1",
                        "zip_code": "123 45"
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

        self._dummy_json_data_1 = {
            "country_code": "se",
            "sigel": "lib1_sigel",
            "statistics": "true",
            "name": "lib1",
            "library_type": "sjukbib",
            "municipality_code": "1793",
            "school_code": None,
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
                    },
                    {
                        "address_type": "stat",
                        "city": "stat_lib1_city",
                        "street": "stat_street1",
                        "zip_code": "123 45"
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
        library = None

        if check_library_criteria(json_data):
            library = library_from_json(json_data)

        self.assertEquals(library.sigel, "lib1_sigel")
        self.assertEquals(library.name, "lib1")
        self.assertEquals(library.city, "stat_lib1_city")
        self.assertEquals(library.address, "stat_street1")
        self.assertEquals(library.email, "lib1@dom.top")
        self.assertEquals(library.municipality_code, "1793")
        self.assertEquals(library.library_type, "sjukbib")
        self.assertEquals(library.zip_code, "123 45")
        self.assertEquals(library.external_identifiers[0].type, "school_code")
        self.assertEquals(library.external_identifiers[0].identifier, "12345678")

    def test_creates_library_from_dict_without_external_id_if_school_code_is_none(self):
        json_data = self._dummy_json_data_1
        library = None

        if check_library_criteria(json_data):
            library = library_from_json(json_data)

        self.assertEquals(library.sigel, "lib1_sigel")
        self.assertEquals(library.name, "lib1")
        self.assertEquals(library.city, "stat_lib1_city")
        self.assertEquals(library.address, "stat_street1")
        self.assertEquals(library.email, "lib1@dom.top")
        self.assertEquals(library.municipality_code, "1793")
        self.assertEquals(library.library_type, "sjukbib")
        self.assertEquals(library.zip_code, "123 45")
        self.assertEquals(library.external_identifiers, None)

    def test_does_not_import_non_swedish_libraries(self):
        json_data = self._dummy_json_data
        json_data["country_code"] = "dk"
        library = None

        if check_library_criteria(json_data):
            library = library_from_json(json_data)

        self.assertEquals(library, None)

    def test_does_not_import_busbib(self):
        json_data = self._dummy_json_data
        json_data["library_type"] = "busbib"
        library = None

        if check_library_criteria(json_data):
            library = library_from_json(json_data)

        self.assertEquals(library, None)

    def test_does_not_import_library_with_invalid_library_type(self):
        json_data = self._dummy_json_data
        json_data["library_type"] = "does_not_exist"
        library = None

        if check_library_criteria(json_data):
            library = library_from_json(json_data)

        self.assertEquals(library, None)

    def test_trims_blank_spaces_from_library_name(self):
        json_data = self._dummy_json_data
        json_data["name"] = "  a b c  "
        library = None

        if check_library_criteria(json_data):
            library = library_from_json(json_data)

        self.assertEquals(library.name, "a b c")

    def test_does_not_library_import_if_no_municipality_code(self):
        json_data = self._dummy_json_data
        json_data.pop("municipality_code")
        library = None

        if check_library_criteria(json_data):
            library = library_from_json(json_data)

        self.assertEquals(library, None)

    def test_does_not_import_non_statistics_library(self):
        json_data = self._dummy_json_data
        json_data.pop("statistics")
        library = None

        if check_library_criteria(json_data):
            library = library_from_json(json_data)

        self.assertEquals(library, None)

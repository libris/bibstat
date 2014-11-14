# -*- coding: UTF-8 -*-

from libstat.tests import MongoTestCase
from libstat.views import _dict_to_library
from libstat.models import Library


class TestLibraryImport(MongoTestCase):

    def setUp(self):
        self._dummy_dict = {
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

    def test_can_not_import_libraries_if_not_logged_in(self):
        self._logout()
        self.assertEquals(len(Library.objects.all()), 0)

        self._get("import_libraries")

        self.assertEquals(len(Library.objects.all()), 0)

    def test_creates_library_from_dict(self):
        dict = self._dummy_dict

        library = _dict_to_library(dict)

        self.assertEquals(library.sigel, "lib1_sigel")
        self.assertEquals(library.name, "lib1")
        self.assertEquals(library.city, "lib1_city")
        self.assertEquals(library.address, "street1")
        self.assertEquals(library.email, "lib1@dom.top")
        self.assertEquals(library.municipality_code, "1793")
        self.assertEquals(library.library_type, "sjukbib")

    def test_does_not_import_non_swedish_libraries(self):
        dict = self._dummy_dict
        dict["country_code"] = "dk"

        library = _dict_to_library(dict)

        self.assertEquals(library, None)

    def test_uses_existing_library_if_sigel_exists(self):
        dict = self._dummy_dict
        existing_library = self._dummy_library(sigel=dict["sigel"])

        imported_library = _dict_to_library(dict)

        self.assertEquals(imported_library.pk, existing_library.pk)


class TestLibraryRemoval(MongoTestCase):

    def setUp(self):
        self._login()

    def test_removes_all_libraries(self):
        self._dummy_library(name="lib1")
        self._dummy_library(name="lib2")
        self._dummy_library(name="lib3")

        self._get("remove_libraries")

        self.assertEquals(len(Library.objects.all()), 0)

    def test_can_not_remove_all_libraries_if_not_logged_in(self):
        self._dummy_library(name="lib1")
        self._dummy_library(name="lib2")
        self._dummy_library(name="lib3")

        self._logout()
        self._get("remove_libraries")

        self.assertEquals(len(Library.objects.all()), 3)

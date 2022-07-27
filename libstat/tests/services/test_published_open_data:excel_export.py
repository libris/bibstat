from libstat.services.excel_export import _published_open_data_as_workbook

from libstat.tests import MongoTestCase


class TestSurveysExport(MongoTestCase):

    def test_can_export_open_data_as_excel(self):
        survey1 = self._dummy_survey()
        survey1.publish()

        response = self._post(action="export",
                              data={"sample_year": "2001"})

        self.assertEqual(response.status_code, 200)

    def test_sets_correct_values_when_exporting_open_data_as_excel(self):
        self._dummy_variable(key="var1")
        self._dummy_observation(variable="var1", value="testvalue")
        library1 = self._dummy_library(name="lib1_name", external_identifiers=[self._dummy_external_identifier(identifier="44444444")])
        survey1 = self._dummy_survey(library=library1)
        survey1.publish()

        worksheet = _published_open_data_as_workbook(2001)

        self.assertEqual(worksheet["A1"].value, "Bibliotek")
        self.assertEqual(worksheet["B1"].value, "Sigel")
        self.assertEqual(worksheet["D1"].value, "Kommunkod")
        self.assertEqual(worksheet["F1"].value, "Externt id")
        self.assertEqual(worksheet["G1"].value, "var1")
        self.assertEqual(worksheet["A2"].value, "lib1_name")
        self.assertEqual(worksheet["F2"].value, "44444444")
        self.assertEqual(worksheet["G2"].value, "testvalue")

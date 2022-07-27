from django.core.management import call_command
from django.core.management.base import CommandError

from libstat.tests import MongoTestCase
from libstat.models import Variable, Survey


class ImportSurveyResponsesTest(MongoTestCase):
    def setUp(self):
        args = []
        opts = {"file": "data/variables/folk_termer.xlsx", "target_group": "folkbib"}
        call_command("import_variables", *args, **opts)

        # Check that all variables have been imported
        self.assertEqual(len(Variable.objects.all()), 201)

    def test_import_survey_responses_requires_file_option(self):
        args = []
        opts = {"target_group": "folkbib", "year": 2012}
        call_command("import_survey_responses", *args, **opts)

        self.assertEqual(len(Survey.objects.all()), 0)

    def test_import_variables_requires_target_group_option(self):
        args = []
        opts = {"file": "libstat/tests/data/Folk2012.xlsx", "year": 2012}
        call_command("import_survey_responses", *args, **opts)

        self.assertEqual(len(Survey.objects.all()), 0)

    def test_import_variables_requires_year_option(self):
        args = []
        opts = {"file": "libstat/tests/data/Folk2012.xlsx", "target_group": "folkbib"}
        call_command("import_survey_responses", *args, **opts)

        self.assertEqual(len(Survey.objects.all()), 0)

    def test_import_survey_responses_should_abort_if_invalid_year(self):
        args = []
        opts = {
            "file": "libstat/tests/data/Folk2012.xlsx",
            "target_group": "folkbib",
            "year": "201b",
        }
        self.assertRaises(
            CommandError, call_command, "import_survey_responses", *args, **opts
        )

    def test_import_survey_responses_should_abort_if_data_for_year_not_in_file(self):
        args = []
        opts = {
            "file": "libstat/tests/data/Folk2012.xlsx",
            "target_group": "folkbib",
            "year": 2013,
        }
        self.assertRaises(
            CommandError, call_command, "import_survey_responses", *args, **opts
        )

    def test_should_import_public_lib_survey_responses(self):
        args = []
        opts = {
            "file": "libstat/tests/data/Folk2012.xlsx",
            "target_group": "folkbib",
            "year": 2012,
        }
        call_command("import_survey_responses", *args, **opts)

        self.assertEqual(len(Survey.objects.all()), 8)

        sr = None
        for s in Survey.objects.all():
            if s.library.name == "KARLSTADS STADSBIBLIOTEK":
                sr = s
        self.assertEqual(sr.library.name, "KARLSTADS STADSBIBLIOTEK")
        self.assertEqual(sr.library.municipality_code, "1780")

        # Check data types and visibility
        # Private, string value
        folk1_obs = [obs for obs in sr.observations if obs.variable.key == "Folk1"][0]
        self.assertTrue(isinstance(folk1_obs.value, str))
        self.assertEqual(folk1_obs.value, "Karlstad")
        self.assertFalse(folk1_obs._is_public)
        # Private, string value None
        folk7_obs = [obs for obs in sr.observations if obs.variable.key == "Folk7"][0]
        self.assertEqual(folk7_obs.value, None)
        self.assertFalse(folk7_obs._is_public)
        # Public, int (boolean) value None
        folk8_obs = [obs for obs in sr.observations if obs.variable.key == "Folk8"][0]
        self.assertEqual(folk8_obs.value, None)
        self.assertTrue(folk8_obs._is_public)
        # Public, decimal value
        folk26_obs = [obs for obs in sr.observations if obs.variable.key == "Folk26"][0]
        self.assertTrue(isinstance(folk26_obs.value, float))
        self.assertEqual(folk26_obs.value, 1798.57575757576)
        self.assertTrue(folk26_obs._is_public)
        # Public, long value
        folk38_obs = [obs for obs in sr.observations if obs.variable.key == "Folk38"][0]
        self.assertTrue(isinstance(folk38_obs.value, int))
        self.assertEqual(folk38_obs.value, 29500000)
        self.assertTrue(folk38_obs._is_public)
        # Public, decimal value (percent)
        folk52_obs = [obs for obs in sr.observations if obs.variable.key == "Folk52"][0]
        self.assertTrue(isinstance(folk52_obs.value, float))
        self.assertEqual(folk52_obs.value, 0.438087421014918)
        self.assertTrue(folk52_obs._is_public)
        # Public, decimal value
        folk54_obs = [obs for obs in sr.observations if obs.variable.key == "Folk54"][0]
        self.assertTrue(isinstance(folk54_obs.value, float))
        self.assertEqual(folk54_obs.value, 8.33583518419239)
        self.assertTrue(folk54_obs._is_public)
        # Private, integer value
        folk201_obs = [obs for obs in sr.observations if obs.variable.key == "Folk201"][
            0
        ]
        self.assertTrue(isinstance(folk201_obs.value, int))
        self.assertEqual(folk201_obs.value, 13057)
        self.assertFalse(folk201_obs._is_public)

        # Check parsing of bool value when 1/1.0/True
        sr2 = Survey.objects.filter(library__name="GISLAVEDS BIBLIOTEK")[0]
        folk8_obs = [obs for obs in sr2.observations if obs.variable.key == "Folk8"][0]
        self.assertTrue(isinstance(folk8_obs.value, bool))
        self.assertEqual(folk8_obs.value, True)

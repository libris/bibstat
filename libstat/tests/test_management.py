# -*- coding: UTF-8 -*-
from django.core.management import call_command
from django.core.management.base import CommandError

from libstat.tests import MongoTestCase
from libstat.models import Variable, Survey


"""
    Management command test cases
"""


class ImportVariablesTest(MongoTestCase):

    def test_import_variables_requires_file_option(self):
        args = []
        opts = {"target_group": "folkbib"}
        call_command('import_variables', *args, **opts)

        self.assertEquals(len(Variable.objects.all()), 0)

    def test_import_variables_requires_target_group_option(self):
        args = []
        opts = {"target_group": "folkbib"}
        call_command('import_variables', *args, **opts)

        self.assertEquals(len(Variable.objects.all()), 0)

    def test_should_import_public_lib_variables(self):
        args = []
        opts = {"file": "data/folk_termer.xlsx", "target_group": "folkbib"}
        call_command('import_variables', *args, **opts)

        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 201)

        folk1 = Variable.objects.filter(key="Folk1")[0]  # Private (by category "Bakgrundsvariabel"), type "Text"
        folk7 = Variable.objects.filter(key="Folk7")[0]  # Private, type "Numerisk"
        folk8 = Variable.objects.filter(key="Folk8")[0]  # Public, type "Boolesk"
        folk26 = Variable.objects.filter(key="Folk26")[0]  # Public, type "Decimal två"
        folk38 = Variable.objects.filter(key="Folk38")[0]  # Public, type "Long"
        folk52 = Variable.objects.filter(key="Folk52")[0]  # Public, type "Procent"
        folk54 = Variable.objects.filter(key="Folk54")[0]  # Public, type "Decimal ett"
        folk201 = Variable.objects.filter(key="Folk201")[0]  # Private, type "Integer", last row

        # Check visibility
        self.assertFalse(folk1.is_public)
        self.assertFalse(folk7.is_public)
        self.assertTrue(folk8.is_public)
        self.assertTrue(folk26.is_public)
        self.assertTrue(folk38.is_public)
        self.assertTrue(folk52.is_public)
        self.assertTrue(folk54.is_public)
        self.assertFalse(folk201.is_public)

        # Check types
        self.assertEquals(folk1.type, u"string")
        self.assertEquals(folk7.type, u"string")
        self.assertEquals(folk8.type, u"boolean")
        self.assertEquals(folk26.type, u"decimal")
        self.assertEquals(folk38.type, u"long")
        self.assertEquals(folk52.type, u"percent")
        self.assertEquals(folk54.type, u"decimal")
        self.assertEquals(folk201.type, u"integer")

    def test_should_update_public_lib_variables(self):
        args = []
        opts = {"file": "data/folk_termer.xlsx", "target_group": "folkbib"}
        call_command('import_variables', *args, **opts)

        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 201)
        # Check target_group before
        self.assertEquals(Variable.objects.filter(key="Folk52")[0].target_groups, [u"folkbib"])

        # Changing target group to avoid having to modify terms file
        args = []
        opts = {"file": "data/folk_termer.xlsx", "target_group": "skolbib"}
        call_command('import_variables', *args, **opts)

        # Check that no new variables have been created
        self.assertEquals(len(Variable.objects.all()), 201)
        # Check target_group after
        self.assertEquals(Variable.objects.filter(key="Folk52")[0].target_groups, [u"skolbib"])

    def test_should_import_research_lib_variables(self):
        args = []
        opts = {"file": "data/forsk_termer.xlsx", "target_group": "specbib"}
        call_command('import_variables', *args, **opts)

        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 163)

        forsk1 = Variable.objects.filter(key="Forsk1")[0]  # Private (by category "Bakgrundsvariabler", type "Text"
        forsk2 = Variable.objects.filter(key="Forsk2")[0]  # Private, type "Integer"
        forsk8 = Variable.objects.filter(key="Forsk8")[0]  # Public, type "Decimal två"
        forsk19 = Variable.objects.filter(key="Forsk19")[0]  # Public, type "Procent"
        forsk29 = Variable.objects.filter(key="Forsk29")[0]  # Public, type "Long"
        forsk154 = Variable.objects.filter(key="Forsk154")[0]  # Public, type "Decimal ett"

        # Check visibility
        self.assertEquals(forsk1.is_public, False)
        self.assertEquals(forsk2.is_public, False)
        self.assertEquals(forsk8.is_public, True)
        self.assertEquals(forsk19.is_public, True)
        self.assertEquals(forsk29.is_public, True)
        self.assertEquals(forsk154.is_public, True)

        # Check types
        self.assertEquals(forsk1.type, u"string")
        self.assertEquals(forsk2.type, u"integer")
        self.assertEquals(forsk8.type, u"decimal")
        self.assertEquals(forsk19.type, u"percent")
        self.assertEquals(forsk29.type, u"long")
        self.assertEquals(forsk154.type, u"decimal")

    def test_should_update_research_lib_variables(self):
        args = []
        opts = {"file": "data/forsk_termer.xlsx", "target_group": "specbib"}
        call_command('import_variables', *args, **opts)

        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 163)
        # Check target_group before
        self.assertEquals(Variable.objects.filter(key="Forsk111")[0].target_groups, ["specbib"])

        # Changing target group to avoid having to modify terms file
        args = []
        opts = {"file": "data/forsk_termer.xlsx", "target_group": "sjukbib"}
        call_command('import_variables', *args, **opts)

        # Check that no new variables have been created
        self.assertEquals(len(Variable.objects.all()), 163)
        # Check target_group after
        self.assertEquals(Variable.objects.filter(key="Forsk111")[0].target_groups, [u"sjukbib"])

    def test_should_import_hospital_lib_variables(self):
        args = []
        opts = {"file": "data/sjukhus_termer.xlsx", "target_group": "sjukbib"}
        call_command('import_variables', *args, **opts)

        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 151)

        sjukhus1 = Variable.objects.filter(key="Sjukhus1")[0]  # Private (by category "Bakgrundsvariabler", type "Text"
        sjukhus9 = Variable.objects.filter(key="Sjukhus9")[0]  # Public, type "Decimal två"
        sjukhus151 = Variable.objects.filter(key="Sjukhus151")[0]  # Private, type "Integer"

        # Check visibility
        self.assertEquals(sjukhus1.is_public, False)
        self.assertEquals(sjukhus9.is_public, True)
        self.assertEquals(sjukhus151.is_public, False)

        # Check types
        self.assertEquals(sjukhus1.type, u"string")
        self.assertEquals(sjukhus9.type, u"decimal")
        self.assertEquals(sjukhus151.type, u"integer")

    def test_should_update_hospital_lib_variables(self):
        args = []
        opts = {"file": "data/sjukhus_termer.xlsx", "target_group": "sjukbib"}
        call_command('import_variables', *args, **opts)

        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 151)
        # Check target_group before
        self.assertEquals(Variable.objects.filter(key="Sjukhus23")[0].target_groups, [u"sjukbib"])

        # Changing target group to avoid having to modify terms file
        args = []
        opts = {"file": "data/sjukhus_termer.xlsx", "target_group": "sjukbib"}
        call_command('import_variables', *args, **opts)

        # Check that no new variables have been created
        self.assertEquals(len(Variable.objects.all()), 151)
        # Check target_group after
        self.assertEquals(Variable.objects.filter(key="Sjukhus23")[0].target_groups, [u"sjukbib"])

    def test_should_import_school_lib_variables(self):
        args = []
        opts = {"file": "data/skol_termer.xlsx", "target_group": "skolbib"}
        call_command('import_variables', *args, **opts)

        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 139)

        skol6 = Variable.objects.filter(key="Skol6")[0]  # Private (by category "Bakgrundsvariabel"), type "Text"
        skol17 = Variable.objects.filter(key="Skol17")[0]  # Private (by category "Bakgrundsvariabel"), type "Numerisk"
        skol41 = Variable.objects.filter(key="Skol41")[0]  # Public, type "Decimal två"
        skol55 = Variable.objects.filter(key="Skol55")[0]  # Private, type "Boolesk"
        skol108 = Variable.objects.filter(key="Skol108")[0]  # Public, type "Integer"

        # Check visibility
        self.assertEquals(skol6.is_public, False)
        self.assertEquals(skol17.is_public, False)
        self.assertEquals(skol41.is_public, True)
        self.assertEquals(skol55.is_public, False)
        self.assertEquals(skol108.is_public, True)

        # Check types
        self.assertEquals(skol6.type, u"string")
        self.assertEquals(skol17.type, u"string")
        self.assertEquals(skol41.type, u"decimal")
        self.assertEquals(skol55.type, u"boolean")
        self.assertEquals(skol108.type, u"integer")

    def test_should_update_school_lib_variables(self):
        args = []
        opts = {"file": "data/skol_termer.xlsx", "target_group": "skolbib"}
        call_command('import_variables', *args, **opts)

        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 139)
        # Check target_group before
        self.assertEquals(Variable.objects.filter(key="Skol5")[0].target_groups, ["skolbib"])

        # Changing target group to avoid having to modify terms file
        args = []
        opts = {"file": "data/skol_termer.xlsx", "target_group": "specbib"}
        call_command('import_variables', *args, **opts)

        # Check that no new variables have been created
        self.assertEquals(len(Variable.objects.all()), 139)
        # Check target_group after
        self.assertEquals(Variable.objects.filter(key="Skol5")[0].target_groups, ["specbib"])


class ImportSurveyResponsesTest(MongoTestCase):

    def setUp(self):
        args = []
        opts = {"file": "data/folk_termer.xlsx", "target_group": "folkbib"}
        call_command('import_variables', *args, **opts)

        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 201)

    def test_import_survey_responses_requires_file_option(self):
        args = []
        opts = {"target_group": "folkbib", "year": 2012}
        call_command('import_survey_responses', *args, **opts)

        self.assertEquals(len(Survey.objects.all()), 0)

    def test_import_variables_requires_target_group_option(self):
        args = []
        opts = {"file": "libstat/tests/data/Folk2012.xlsx", "year": 2012}
        call_command('import_survey_responses', *args, **opts)

        self.assertEquals(len(Survey.objects.all()), 0)

    def test_import_variables_requires_year_option(self):
        args = []
        opts = {"file": "libstat/tests/data/Folk2012.xlsx", "target_group": "folkbib"}
        call_command('import_survey_responses', *args, **opts)

        self.assertEquals(len(Survey.objects.all()), 0)

    def test_import_survey_responses_should_abort_if_invalid_year(self):
        args = []
        opts = {"file": "libstat/tests/data/Folk2012.xlsx", "target_group": "folkbib", "year": '201b'}
        self.assertRaises(CommandError, call_command, 'import_survey_responses', *args, **opts)

    def test_import_survey_responses_should_abort_if_data_for_year_not_in_file(self):
        args = []
        opts = {"file": "libstat/tests/data/Folk2012.xlsx", "target_group": "folkbib", "year": 2013}
        self.assertRaises(CommandError, call_command, 'import_survey_responses', *args, **opts)

    def test_should_import_public_lib_survey_responses(self):
        args = []
        opts = {"file": "libstat/tests/data/Folk2012.xlsx", "target_group": "folkbib", "year": 2012}
        call_command('import_survey_responses', *args, **opts)

        self.assertEquals(len(Survey.objects.all()), 288)

        sr = None
        for s in Survey.objects.all():
            if s.library.name == u"KARLSTADS STADSBIBLIOTEK":
                sr = s
        self.assertEquals(sr.library.name, u"KARLSTADS STADSBIBLIOTEK")

        # Check data types and visibility
        # Private, string value
        folk1_obs = [obs for obs in sr.observations if obs.variable.key == "Folk1"][0]
        self.assertTrue(isinstance(folk1_obs.value, basestring))
        self.assertEquals(folk1_obs.value, u"Karlstad")
        self.assertFalse(folk1_obs._is_public)
        # Private, string value None
        folk7_obs = [obs for obs in sr.observations if obs.variable.key == "Folk7"][0]
        self.assertEquals(folk7_obs.value, None)
        self.assertFalse(folk7_obs._is_public)
        # Public, int (boolean) value None
        folk8_obs = [obs for obs in sr.observations if obs.variable.key == "Folk8"][0]
        self.assertEquals(folk8_obs.value, None)
        self.assertTrue(folk8_obs._is_public)
        # Public, decimal value
        folk26_obs = [obs for obs in sr.observations if obs.variable.key == "Folk26"][0]
        self.assertTrue(isinstance(folk26_obs.value, float))
        self.assertEquals(folk26_obs.value, 1798.57575757576)
        self.assertTrue(folk26_obs._is_public)
        # Public, long value
        folk38_obs = [obs for obs in sr.observations if obs.variable.key == "Folk38"][0]
        self.assertTrue(isinstance(folk38_obs.value, long))
        self.assertEquals(folk38_obs.value, 29500000)
        self.assertTrue(folk38_obs._is_public)
        # Public, decimal value (percent)
        folk52_obs = [obs for obs in sr.observations if obs.variable.key == "Folk52"][0]
        self.assertTrue(isinstance(folk52_obs.value, float))
        self.assertEquals(folk52_obs.value, 0.438087421014918)
        self.assertTrue(folk52_obs._is_public)
        # Public, decimal value
        folk54_obs = [obs for obs in sr.observations if obs.variable.key == "Folk54"][0]
        self.assertTrue(isinstance(folk54_obs.value, float))
        self.assertEquals(folk54_obs.value, 8.33583518419239)
        self.assertTrue(folk54_obs._is_public)
        # Private, integer value
        folk201_obs = [obs for obs in sr.observations if obs.variable.key == "Folk201"][0]
        self.assertTrue(isinstance(folk201_obs.value, int))
        self.assertEquals(folk201_obs.value, 13057)
        self.assertFalse(folk201_obs._is_public)

        # Check parsing of bool value when 1/1.0/True
        sr2 = Survey.objects.filter(library_name=u"GISLAVEDS BIBLIOTEK")[0]
        folk8_obs = [obs for obs in sr2.observations if obs.variable.key == "Folk8"][0]
        self.assertTrue(isinstance(folk8_obs.value, bool))
        self.assertEquals(folk8_obs.value, True)

    def test_import_survey_responses_with_library_lookup(self):
        args = []
        opts = {"file": "libstat/tests/data/Folk2012.xlsx",
                "target_group": "folkbib", "year": 2012, "use_bibdb": "True"}
        call_command('import_survey_responses', *args, **opts)

        self.assertEquals(len(Survey.objects.all()), 288)
        self.assertTrue(Survey.objects.filter(library_name=u"KARLSTADS STADSBIBLIOTEK")[0].library != None)

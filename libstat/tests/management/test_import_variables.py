# -*- coding: UTF-8 -*-
from django.core.management import call_command

from libstat.tests import MongoTestCase
from libstat.models import Variable


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
        opts = {"file": "data/variables/folk_termer.xlsx", "target_group": "folkbib"}
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
        opts = {"file": "data/variables/folk_termer.xlsx", "target_group": "folkbib"}
        call_command('import_variables', *args, **opts)

        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 201)
        # Check target_group before
        self.assertEquals(Variable.objects.filter(key="Folk52")[0].target_groups, [u"folkbib"])

        # Changing target group to avoid having to modify terms file
        args = []
        opts = {"file": "data/variables/folk_termer.xlsx", "target_group": "skolbib"}
        call_command('import_variables', *args, **opts)

        # Check that no new variables have been created
        self.assertEquals(len(Variable.objects.all()), 201)
        # Check target_group after
        self.assertEquals(Variable.objects.filter(key="Folk52")[0].target_groups, [u"skolbib"])

    def test_should_import_research_lib_variables(self):
        args = []
        opts = {"file": "data/variables/forsk_termer.xlsx", "target_group": "specbib"}
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
        opts = {"file": "data/variables/forsk_termer.xlsx", "target_group": "specbib"}
        call_command('import_variables', *args, **opts)

        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 163)
        # Check target_group before
        self.assertEquals(Variable.objects.filter(key="Forsk111")[0].target_groups, ["specbib"])

        # Changing target group to avoid having to modify terms file
        args = []
        opts = {"file": "data/variables/forsk_termer.xlsx", "target_group": "sjukbib"}
        call_command('import_variables', *args, **opts)

        # Check that no new variables have been created
        self.assertEquals(len(Variable.objects.all()), 163)
        # Check target_group after
        self.assertEquals(Variable.objects.filter(key="Forsk111")[0].target_groups, [u"sjukbib"])

    def test_should_import_hospital_lib_variables(self):
        args = []
        opts = {"file": "data/variables/sjukhus_termer.xlsx", "target_group": "sjukbib"}
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
        opts = {"file": "data/variables/sjukhus_termer.xlsx", "target_group": "sjukbib"}
        call_command('import_variables', *args, **opts)

        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 151)
        # Check target_group before
        self.assertEquals(Variable.objects.filter(key="Sjukhus23")[0].target_groups, [u"sjukbib"])

        # Changing target group to avoid having to modify terms file
        args = []
        opts = {"file": "data/variables/sjukhus_termer.xlsx", "target_group": "sjukbib"}
        call_command('import_variables', *args, **opts)

        # Check that no new variables have been created
        self.assertEquals(len(Variable.objects.all()), 151)
        # Check target_group after
        self.assertEquals(Variable.objects.filter(key="Sjukhus23")[0].target_groups, [u"sjukbib"])

    def test_should_import_school_lib_variables(self):
        args = []
        opts = {"file": "data/variables/skol_termer.xlsx", "target_group": "skolbib"}
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
        opts = {"file": "data/variables/skol_termer.xlsx", "target_group": "skolbib"}
        call_command('import_variables', *args, **opts)

        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 139)
        # Check target_group before
        self.assertEquals(Variable.objects.filter(key="Skol5")[0].target_groups, ["skolbib"])

        # Changing target group to avoid having to modify terms file
        args = []
        opts = {"file": "data/variables/skol_termer.xlsx", "target_group": "specbib"}
        call_command('import_variables', *args, **opts)

        # Check that no new variables have been created
        self.assertEquals(len(Variable.objects.all()), 139)
        # Check target_group after
        self.assertEquals(Variable.objects.filter(key="Skol5")[0].target_groups, ["specbib"])

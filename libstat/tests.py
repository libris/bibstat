# -*- coding: UTF-8 -*-
from django.test.simple import DjangoTestSuiteRunner
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.core.management.base import CommandError

from datetime import datetime
import json

from libstat.models import Variable, OpenData, SurveyResponse, SurveyObservation, Library
from libstat.utils import parse_datetime_from_isodate_str
from libstat.apis import data_context, term_context

"""
    Test case and test runner for use with Mongoengine
""" 
class MongoEngineTestRunner(DjangoTestSuiteRunner):
    def setup_databases(self):
        pass
        
    def teardown_databases(self, *args):
        pass
 
class MongoTestCase(TestCase):
    mongodb_name = 'test_%s' % settings.MONGODB_NAME
    
    def _fixture_setup(self):
        from mongoengine.connection import connect, disconnect
        disconnect()
        connect(self.mongodb_name)
        from mongoengine.django.mongo_auth.models import MongoUser
        MongoUser.objects.create_superuser("admin", "admin@example.com", "admin")
        
#     def _fixture_teardown(self):
#         pass
    
    def _post_teardown(self):
        from mongoengine.connection import get_connection, disconnect
        connection = get_connection()
        connection.drop_database(self.mongodb_name)
        disconnect()

"""
    Management command test cases
"""
class ImportVariablesTest(MongoTestCase):

    def test_import_variables_requires_file_option(self):
        args = []
        opts = {"target_group": "public"}
        call_command('import_variables', *args, **opts)
        
        self.assertEquals(len(Variable.objects.all()), 0)


    def test_import_variables_requires_target_group_option(self):
        args = []
        opts = {"target_group": "public"}
        call_command('import_variables', *args, **opts)
        
        self.assertEquals(len(Variable.objects.all()), 0)
    
    
    def test_should_import_public_lib_variables(self):
        args = []
        opts = {"file": "data/folk_termer.xlsx", "target_group": "public"}
        call_command('import_variables', *args, **opts)
        
        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 201)
        
        folk1 = Variable.objects.filter(key="Folk1")[0] # Private (by category "Bakgrundsvariabel"), type "Text"
        folk7 = Variable.objects.filter(key="Folk7")[0] # Private, type "Numerisk"
        folk8 = Variable.objects.filter(key="Folk8")[0] # Public, type "Boolesk"
        folk26 = Variable.objects.filter(key="Folk26")[0] # Public, type "Decimal två"
        folk38 = Variable.objects.filter(key="Folk38")[0] # Public, type "Long"
        folk52 = Variable.objects.filter(key="Folk52")[0] # Public, type "Procent"
        folk54 = Variable.objects.filter(key="Folk54")[0] # Public, type "Decimal ett"
        folk201 = Variable.objects.filter(key="Folk201")[0] # Private, type "Integer", last row
        
        #  Check visibility
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
        opts = {"file": "data/folk_termer.xlsx", "target_group": "public"}
        call_command('import_variables', *args, **opts)
        
        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 201)
        # Check target_group before
        self.assertEquals(Variable.objects.filter(key="Folk52")[0].target_groups, [u"public"])

        # Changing target group to avoid having to modify terms file
        args = []
        opts = {"file": "data/folk_termer.xlsx", "target_group": "school"}
        call_command('import_variables', *args, **opts)
        
        # Check that no new variables have been created
        self.assertEquals(len(Variable.objects.all()), 201)
         # Check target_group after
        self.assertEquals(Variable.objects.filter(key="Folk52")[0].target_groups, [u"school"])
        
        
    def test_should_import_research_lib_variables(self):
        args = []
        opts = {"file": "data/forsk_termer.xlsx", "target_group": "research"}
        call_command('import_variables', *args, **opts)
        
        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 163)
        
        forsk1 = Variable.objects.filter(key="Forsk1")[0] # Private (by category "Bakgrundsvariabler", type "Text"
        forsk2 = Variable.objects.filter(key="Forsk2")[0] # Private, type "Integer"
        forsk8 = Variable.objects.filter(key="Forsk8")[0] # Public, type "Decimal två"
        forsk19 = Variable.objects.filter(key="Forsk19")[0] # Public, type "Procent"
        forsk29 = Variable.objects.filter(key="Forsk29")[0] # Public, type "Long"
        forsk154 = Variable.objects.filter(key="Forsk154")[0] # Public, type "Decimal ett"
        
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
        opts = {"file": "data/forsk_termer.xlsx", "target_group": "research"}
        call_command('import_variables', *args, **opts)
        
        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 163)
        # Check target_group before
        self.assertEquals(Variable.objects.filter(key="Forsk111")[0].target_groups, [u"research"])
        
        # Changing target group to avoid having to modify terms file
        args = []
        opts = {"file": "data/forsk_termer.xlsx", "target_group": "hospital"}
        call_command('import_variables', *args, **opts)
        
        # Check that no new variables have been created
        self.assertEquals(len(Variable.objects.all()), 163)
        # Check target_group after
        self.assertEquals(Variable.objects.filter(key="Forsk111")[0].target_groups, [u"hospital"]) 
        
    def test_should_import_hospital_lib_variables(self):
        args = []
        opts = {"file": "data/sjukhus_termer.xlsx", "target_group": "hospital"}
        call_command('import_variables', *args, **opts)
        
        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 151)
        
        sjukhus1 = Variable.objects.filter(key="Sjukhus1")[0] # Private (by category "Bakgrundsvariabler", type "Text"
        sjukhus9 = Variable.objects.filter(key="Sjukhus9")[0] # Public, type "Decimal två"
        sjukhus151 = Variable.objects.filter(key="Sjukhus151")[0] # Private, type "Integer"
         
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
        opts = {"file": "data/sjukhus_termer.xlsx", "target_group": "hospital"}
        call_command('import_variables', *args, **opts)
        
        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 151)
        # Check target_group before
        self.assertEquals(Variable.objects.filter(key="Sjukhus23")[0].target_groups, [u"hospital"])
        
        # Changing target group to avoid having to modify terms file
        args = []
        opts = {"file": "data/sjukhus_termer.xlsx", "target_group": "hospital"}
        call_command('import_variables', *args, **opts)
        
         # Check that no new variables have been created
        self.assertEquals(len(Variable.objects.all()), 151)
        # Check target_group after
        self.assertEquals(Variable.objects.filter(key="Sjukhus23")[0].target_groups, [u"hospital"])
        
    def test_should_import_school_lib_variables(self):
        args = []
        opts = {"file": "data/skol_termer.xlsx", "target_group": "school"}
        call_command('import_variables', *args, **opts)
        
        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 139)
        
        skol6 = Variable.objects.filter(key="Skol6")[0] # Private (by category "Bakgrundsvariabel"), type "Text"
        skol17 = Variable.objects.filter(key="Skol17")[0] # Private (by category "Bakgrundsvariabel"), type "Numerisk"
        skol41 = Variable.objects.filter(key="Skol41")[0] # Public, type "Decimal två"
        skol55 = Variable.objects.filter(key="Skol55")[0] # Private, type "Boolesk"
        skol108 = Variable.objects.filter(key="Skol108")[0] # Public, type "Integer"
        
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
        opts = {"file": "data/skol_termer.xlsx", "target_group": "school"}
        call_command('import_variables', *args, **opts)
        
        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 139)
        # Check target_group before
        self.assertEquals(Variable.objects.filter(key="Skol5")[0].target_groups, [u"school"])
        
        # Changing target group to avoid having to modify terms file
        args = []
        opts = {"file": "data/skol_termer.xlsx", "target_group": "research"}
        call_command('import_variables', *args, **opts)
        
        # Check that no new variables have been created
        self.assertEquals(len(Variable.objects.all()), 139)
        # Check target_group after
        self.assertEquals(Variable.objects.filter(key="Skol5")[0].target_groups, [u"research"])
        

class ImportSurveyResponsesTest(MongoTestCase):
    def setUp(self):
        args = []
        opts = {"file": "data/folk_termer.xlsx", "target_group": "public"}
        call_command('import_variables', *args, **opts)
        
        # Check that all variables have been imported
        self.assertEquals(len(Variable.objects.all()), 201)
        
    def test_import_survey_responses_requires_file_option(self):
        args = []
        opts = {"target_group": "public", "year": 2012}
        call_command('import_survey_responses', *args, **opts)
        
        self.assertEquals(len(SurveyResponse.objects.all()), 0)


    def test_import_variables_requires_target_group_option(self):
        args = []
        opts = {"file": "libstat/tests/data/Folk2012.xlsx", "year": 2012}
        call_command('import_survey_responses', *args, **opts)
        
        self.assertEquals(len(SurveyResponse.objects.all()), 0)
    
    def test_import_variables_requires_year_option(self):
        args = []
        opts = {"file": "libstat/tests/data/Folk2012.xlsx", "target_group": "public"}
        call_command('import_survey_responses', *args, **opts)
        
        self.assertEquals(len(SurveyResponse.objects.all()), 0)
        
    def test_import_survey_responses_should_abort_if_invalid_year(self):
        args = []
        opts = {"file": "libstat/tests/data/Folk2012.xlsx", "target_group": "public", "year": '201b'}
        self.assertRaises(CommandError, call_command, 'import_survey_responses', *args, **opts)
    
    def test_import_survey_responses_should_abort_if_data_for_year_not_in_file(self):
        args = []
        opts = {"file": "libstat/tests/data/Folk2012.xlsx", "target_group": "public", "year": 2013}
        self.assertRaises(CommandError, call_command, 'import_survey_responses', *args, **opts)
    
    def test_should_import_public_lib_survey_responses(self):
        args = []
        opts = {"file": "libstat/tests/data/Folk2012.xlsx", "target_group": "public", "year": 2012}
        call_command('import_survey_responses', *args, **opts)
        
        self.assertEquals(len(SurveyResponse.objects.all()), 288)
        sr = SurveyResponse.objects.filter(library_name=u"KARLSTADS STADSBIBLIOTEK")[0]
        self.assertTrue(sr.library == None)
        
        ## Check data types and visibility
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
        sr2 = SurveyResponse.objects.filter(library_name=u"GISLAVEDS BIBLIOTEK")[0]
        folk8_obs = [obs for obs in sr2.observations if obs.variable.key == "Folk8"][0]
        self.assertTrue(isinstance(folk8_obs.value, bool))
        self.assertEquals(folk8_obs.value, True)
        
    def test_import_survey_responses_with_library_lookup(self):
        args = []
        opts = {"file": "libstat/tests/data/Folk2012.xlsx", "target_group": "public", "year": 2012, "use_bibdb": "True"}
        call_command('import_survey_responses', *args, **opts)
        
        self.assertEquals(len(SurveyResponse.objects.all()), 288)
        self.assertTrue(SurveyResponse.objects.filter(library_name=u"KARLSTADS STADSBIBLIOTEK")[0].library != None)

        
"""
    Util functions test cases
"""
class UtilsTest(MongoTestCase):
    def test_should_parse_datetime_from_isodate_str(self):
        self.assertEquals(parse_datetime_from_isodate_str("2014-06-03T15:47:22.873+02:00"), None)
        self.assertEquals(parse_datetime_from_isodate_str("2014-06-03T15:47:22.873Z"), None)
        self.assertEquals(parse_datetime_from_isodate_str("2014-06-03T15:47:22.873"), datetime(2014, 06, 03, 15, 47, 22, 873000))
        self.assertEquals(parse_datetime_from_isodate_str("2014-06-03T15:47:22"), datetime(2014, 06, 03, 15, 47, 22))
        self.assertEquals(parse_datetime_from_isodate_str("2014-06-03T15:47"), datetime(2014, 06, 03, 15, 47))
        self.assertEquals(parse_datetime_from_isodate_str("2014-06-03T15"), datetime(2014, 06, 03, 15))
        self.assertEquals(parse_datetime_from_isodate_str("2014-06-03"), datetime(2014, 06, 03))
        self.assertEquals(parse_datetime_from_isodate_str("2014-06"), datetime(2014, 06, 01))
        self.assertEquals(parse_datetime_from_isodate_str("2014"), datetime(2014, 01, 01))
        self.assertEquals(parse_datetime_from_isodate_str("jun 3 2014"), None)
        


"""
    Model class test cases
"""
class SurveyResponseTest(MongoTestCase):
    def setUp(self):
        v1 = Variable(key=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", type="integer", is_public=True, target_groups=["public"])
        v1.save()
        v2 = Variable(key=u"folk6", description=u"Är huvudbiblioteket i er kommun integrerat med ett skolbibliotek? 1=ja", type="boolean", is_public=True, target_groups=["public"])
        v2.save()
        v3 = Variable(key=u"folk8", description=u"Textkommentar", type="string", is_public=False, target_groups=["public"])
        v3.save()
        sr = SurveyResponse(library_name="KARLSTAD STADSBIBLIOTEK", sample_year=2013, target_group="public", observations=[])
        sr.library = Library(bibdb_id=u"323", bibdb_sigel="Kld1", bibdb_name=u"Karlstad stadsbibliotek")
        sr.observations.append(SurveyObservation(variable=v1, value=7, _source_key="folk5", _is_public=v1.is_public))
        sr.observations.append(SurveyObservation(variable=v2, value=None, _source_key="folk6", _is_public=v2.is_public))
        sr.observations.append(SurveyObservation(variable=v3, value=u"Här är en kommentar", _source_key="folk8", _is_public=v3.is_public))
        sr.save()
        
    
    def test_should_export_public_non_null_observations_to_openData(self):
        survey_response = SurveyResponse.objects.first()
        survey_response.publish()
        
        data = OpenData.objects.all()
        self.assertEquals(len(data), 1)
        
        open_data = data.get(0)
        self.assertEquals(open_data.library_name, "KARLSTAD STADSBIBLIOTEK")
        self.assertEquals(open_data.library_id, "323")
        self.assertEquals(open_data.sample_year, 2013)
        self.assertEquals(open_data.variable.key, "folk5")
        self.assertEquals(open_data.target_group, "public")
        self.assertEquals(open_data.value, 7)
        self.assertTrue(open_data.date_modified)
        self.assertTrue(open_data.date_created)
        self.assertEquals(open_data.date_created, open_data.date_modified)
    
    def test_should_overwrite_value_and_date_modified_for_existing_openData(self):
        survey_response = SurveyResponse.objects.first()
        survey_response.publish()

        for obs in survey_response.observations:
            if obs.variable.key == "folk5":
                obs.value = 9
        survey_response.save()
        survey_response.publish()
        
        data = OpenData.objects.all()
        self.assertEquals(len(data), 1)
        
        open_data = data.get(0)
        self.assertEquals(open_data.library_name, "KARLSTAD STADSBIBLIOTEK")
        self.assertEquals(open_data.library_id, "323")
        self.assertEquals(open_data.sample_year, 2013)
        self.assertEquals(open_data.variable.key, "folk5")
        self.assertEquals(open_data.target_group, "public")
        self.assertEquals(open_data.value, 9)
        self.assertTrue(open_data.date_modified)
        self.assertTrue(open_data.date_created)
        self.assertNotEquals(open_data.date_created, open_data.date_modified)
        
    
class OpenDataTest(MongoTestCase):
    def setUp(self):
        v = Variable(key=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", type="integer", is_public=True, target_groups=["public"])
        v.save()
        publishing_date = datetime(2014, 06, 03, 15, 28, 31)
        d1 = OpenData(library_name=u"KARLSTAD STADSBIBLIOTEK", library_id=u"323", sample_year=2013, target_group="public", variable=v, value=6, date_created=publishing_date, date_modified=publishing_date)
        d1.save()
        d2 = OpenData(library_name=u"NORRBOTTENS LÄNSBIBLIOTEK", sample_year=2013, target_group="public", variable=v, value=6, date_created=publishing_date, date_modified=publishing_date)
        d2.save()
        
    def test_should_transform_object_with_library_id_to_dict(self):
       object = OpenData.objects.get(library_name=u"KARLSTAD STADSBIBLIOTEK")
       openDataAsDict = {
            u"@id": str(object.id),
            u"@type": u"Observation",
            u"folk5": 6, 
            u"library": {u"@id": u"{}/library/323".format(settings.BIBDB_BASE_URL)},
            u"sampleYear": 2013,
            u"targetGroup": u"Folkbibliotek",
            # u"targetGroup": {u"@id": u"public"}, #TODO
            u"published": "2014-06-03T15:28:31.000000Z",
            u"modified": "2014-06-03T15:28:31.000000Z" 
       }
       self.assertEquals(object.to_dict(), openDataAsDict)
    
    def test_should_transform_object_without_library_id_to_dict(self):
       object = OpenData.objects.get(library_name=u"NORRBOTTENS LÄNSBIBLIOTEK")
       openDataAsDict = {
            u"@id": str(object.id),
            u"@type": u"Observation",
            u"folk5": 6, 
            u"library": {u"name": u"NORRBOTTENS LÄNSBIBLIOTEK"},
            u"sampleYear": 2013,
            u"targetGroup": u"Folkbibliotek",
            # u"targetGroup": {u"@id": u"public"}, #TODO
            u"published": "2014-06-03T15:28:31.000000Z",
            u"modified": "2014-06-03T15:28:31.000000Z" 
       }
       self.assertEquals(object.to_dict(), openDataAsDict)
       
       
class VariableTest(MongoTestCase):
    def setUp(self):
        self.v = Variable(key=u"Folk10", description=u"Antal bemannade servicesställen", type="integer", is_public=True, target_groups=["public"])
        self.v.save()
        
        self.v2 = Variable(key=u"Folk35", description=u"Antal årsverken övrig personal", type="decimal", is_public=True, target_groups=["public"])
        self.v2.question = u"Hur många årsverken utfördes av personal i folkbiblioteksverksamheten under 2012?"
        self.v2.question_part = u"Antal årsverken övrig personal (ej städpersonal)"
        self.v2.save()
        
        self.v3 = Variable(key=u"Folk31", description=u"Antal årsverken totalt", type="decimal", is_public=True, target_groups=["public"])
        self.v3.summary_of = [self.v2]
        self.v3.save()
        
        self.v4 = Variable(key=u"Folk69", description=u"Totalt nyförvärv AV-medier", type="integer", is_public=True, target_groups=["public"])
        self.v4.question = u"Hur många nyförvärv av AV-media gjordes under 2012?"
        self.v4.save()
        
    
    def test_should_transform_object_to_dict(self):
        folk10 = Variable.objects.get(pk=self.v.id)
        expectedVariableDict = {
            u"@id": u"Folk10",
            u"@type": [u"rdf:Property", u"qb:MeasureProperty"],
            u"comment": u"Antal bemannade servicesställen",
            u"range": u"xsd:integer"
        }
        self.assertEqual(folk10.to_dict(), expectedVariableDict)
    
    def test_variable_should_have_question_and_question_part(self):
        folk35 = Variable.objects.get(pk=self.v2.id)
        self.assertTrue(hasattr(folk35, "question") and folk35.question == u"Hur många årsverken utfördes av personal i folkbiblioteksverksamheten under 2012?")
        self.assertTrue(hasattr(folk35, "question_part") and folk35.question_part == u"Antal årsverken övrig personal (ej städpersonal)")
        
    def test_summary_variable_without_question_or_question_part_is_summary_auto_field(self):
        folk31 = Variable.objects.get(pk=self.v3.id)
        self.assertTrue(folk31.is_summary_auto_field)
        # THis field is automatically summarized in survey and the user cannot change the value
        
    def test_summary_variable_with_question_or_question_part_is_summary_field(self):
        folk69 = Variable.objects.get(pk=self.v4.id)
        self.assertFalse(folk69.is_summary_auto_field)
        # This field is automatically summarized in survey, but value can be changed by user.
        # TODO: Maybe a is_summary_field helper property on model could for this state?
    
    
    
"""
    API test cases
"""
class OpenDataApiTest(MongoTestCase):
    def setUp(self):
        v1 = Variable(key=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", type="integer", is_public=True, target_groups=["public"])
        v1.save()
        v2 = Variable(key=u"folk6", description=u"Är huvudbiblioteket i er kommun integrerat med ett skolbibliotek? 1=ja", type="integer", is_public=True, target_groups=["public"])
        v2.save()
        
        creation_date = datetime(2014, 05, 27, 8, 00, 00)
        date1 = datetime(2014, 06, 02, 17, 57, 16)
        d1 = OpenData(library_name=u"NORRBOTTENS LÄNSBIBLIOTEK", library_id=u"81", sample_year=2013, target_group="public", variable=v1, value=7, date_created=creation_date, date_modified=date1)
        d1.save()
        
        date1 = datetime(2014, 06, 03, 15, 28, 31)
        d1 = OpenData(library_name=u"KARLSTAD STADSBIBLIOTEK", library_id=u"323", sample_year=2013, target_group="public", variable=v1, value=6, date_created=creation_date, date_modified=date1)
        d1.save()
        
        date2 = datetime(2014, 06, 04, 11, 14, 01)
        d2 = OpenData(library_name=u"GRÄNNA BIBLIOTEK", library_id=u"11070", sample_year=2013, target_group="public", variable=v2, value=1, date_created=creation_date, date_modified=date2)
        d2.save()
    
    def test_response_should_return_jsonld(self):
        response = self.client.get(reverse("data_api"))
        self.assertEqual(response["Content-Type"], "application/ld+json")
        
    def test_response_should_contain_context(self):
        response = self.client.get(reverse("data_api"))
        data = json.loads(response.content)
        self.assertEquals(data[u"@context"], data_context)
    
    def test_should_not_filter_by_date_unless_requested(self):
        response = self.client.get(reverse("data_api"))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 3)

    def test_should_filter_data_by_from_date(self):
        response = self.client.get(u"{}?from_date=2014-06-04".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"][u"@id"], u"{}/library/11070".format(settings.BIBDB_BASE_URL))
    
    def test_should_filter_data_by_to_date(self):
        response = self.client.get(u"{}?to_date=2014-06-03".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"][u"@id"], u"{}/library/81".format(settings.BIBDB_BASE_URL))
        
    def test_should_filter_data_by_date_range(self):
        response = self.client.get(u"{}?from_date=2014-06-03T15:28:31.000&to_date=2014-06-04T11:14:00.000".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"][u"@id"], u"{}/library/323".format(settings.BIBDB_BASE_URL))
    
    def test_should_limit_results(self):
        response = self.client.get(u"{}?limit=2".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 2)
        
    def test_should_limit_results_with_offset(self):
        response = self.client.get(u"{}?limit=2&offset=2".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 1)
        
    def test_should_filter_by_term_key(self):
        response = self.client.get(u"{}?term=folk6".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"folk6"], 1)
        
    def test_should_return_empty_result_if_unknown_term(self):
        response = self.client.get(u"{}?term=hej".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 0)
        

class ObservationApiTest(MongoTestCase):
    def setUp(self):
        v1 = Variable(key=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", type="integer", is_public=True, target_groups=["public"])
        v1.save()
        date1 = datetime(2014, 06, 02, 17, 57, 16)
        obs = OpenData(library_name=u"NORRBOTTENS LÄNSBIBLIOTEK", library_id=u"81", sample_year=2013, target_group="public", variable=v1, value=7, date_created=date1, date_modified=date1)
        obs.save()
   
    def test_response_should_return_jsonld(self):
        obs = OpenData.objects.first()
        response = self.client.get(reverse("observation_api", kwargs={ "observation_id": str(obs.id)}))
        self.assertEqual(response["Content-Type"], "application/ld+json")
        
    def test_response_should_contain_context(self):
        obs = OpenData.objects.first()
        response = self.client.get(reverse("observation_api", kwargs={ "observation_id": str(obs.id)}))
        data = json.loads(response.content)
        self.assertEqual(data[u"@context"][u"@vocab"], u"{}/def/terms/".format(settings.API_BASE_URL)),
        self.assertEquals(data[u"@context"][u"@base"], u"{}/data/".format(settings.API_BASE_URL))
        
    def test_should_return_one_observation(self):
        obs = OpenData.objects.first()
        response = self.client.get(reverse("observation_api", kwargs={ "observation_id": str(obs.id)}))
        data = json.loads(response.content)
        self.assertEqual(data[u"@id"], str(obs.id))
        self.assertEqual(data[u"@type"], u"Observation")
        self.assertEqual(data[u"folk5"], obs.value)
        self.assertEqual(data[u"library"], {u"@id": u"{}/library/{}".format(settings.BIBDB_BASE_URL, obs.library_id)})
        self.assertEqual(data[u"sampleYear"], obs.sample_year)
        self.assertEqual(data[u"published"], obs.date_created_str())
        self.assertEqual(data[u"modified"], obs.date_modified_str())
    
    def test_should_return_404_if_observation_not_found(self):
        response = self.client.get(reverse("observation_api", kwargs={ "observation_id": "12323873982375a8c0g"}))
        self.assertEqual(response.status_code, 404)

        
class TermsApiTest(MongoTestCase):
    def setUp(self):
        v = Variable(key=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", type="integer", is_public=True, target_groups=["public"])
        v.save()
    
    def test_response_should_return_jsonld(self):
        response = self.client.get(reverse("terms_api"))
        self.assertEqual(response["Content-Type"], "application/ld+json")
    
    def test_response_should_contain_context(self):
        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)
        self.assertEquals(data[u"@context"], term_context)
        
    def test_should_contain_hardcoded_terms(self):
        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)
        ids = [term[u"@id"] for term in data[u"terms"]]
        self.assertTrue(u"library" in ids)
        self.assertTrue(u"sampleYear" in ids)
        self.assertTrue(u"targetGroup" in ids)
        self.assertTrue(u"modified" in ids)
        self.assertTrue(u"published" in ids)
        self.assertTrue(u"Observation" in ids)
    
    def test_should_return_all_variables(self):
        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)
        ids = [term[u"@id"] for term in data[u"terms"]]
        self.assertTrue(u"folk5" in ids)
        
        
class TermApiTest(MongoTestCase):
    def setUp(self):
        v1 = Variable(key=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", type="integer", is_public=True, target_groups=["public"])
        v1.save()
        v2 = Variable(key=u"folk6", description=u"Är huvudbiblioteket i er kommun integrerat med ett skolbibliotek? 1=ja", type="integer", is_public=True, target_groups=["public"])
        v2.save()
    
    def test_response_should_return_jsonld(self):
        response = self.client.get(reverse("term_api", kwargs={ "term_key": "folk5"}))
        self.assertEqual(response["Content-Type"], "application/ld+json")
        
    def test_response_should_contain_context(self):
        response = self.client.get(reverse("term_api", kwargs={ "term_key": "folk5"}))
        data = json.loads(response.content)
        self.assertEqual(data[u"@context"][u"xsd"], u"http://www.w3.org/2001/XMLSchema#")
        self.assertEqual(data[u"@context"][u"rdf"], u"http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.assertEqual(data[u"@context"][u"rdfs"], u"http://www.w3.org/2000/01/rdf-schema#")
        self.assertEqual(data[u"@context"][u"qb"], u"http://purl.org/linked-data/cube#")
        self.assertEqual(data[u"@context"][u"@language"], u"sv")
        self.assertEqual(data[u"@context"][u"label"], u"rdfs:label")
        self.assertEqual(data[u"@context"][u"range"], {u"@id": u"rdfs:range", u"@type": u"@id"})
        self.assertEqual(data[u"@context"][u"comment"], u"rdfs:comment")
        self.assertEqual(data[u"@context"][u"subClassOf"], {u"@id": u"rdfs:subClassOf", u"@type": u"@id"})  
        
    def test_should_return_one_term(self):
        response = self.client.get(reverse("term_api", kwargs={ "term_key": "folk5"}))
        data = json.loads(response.content)
        self.assertEquals(len(data), 6)
        self.assertEquals(data[u"@context"], term_context)
        self.assertEquals(data[u"@id"], u"folk5"),
        self.assertEquals(data[u"@type"], [u"rdf:Property", u"qb:MeasureProperty"]),
        self.assertEquals(data[u"comment"], u"Antal bemannade serviceställen, sammanräknat"),
        self.assertEquals(data[u"range"], u"xsd:integer")
        self.assertEquals(data[u"isDefinedBy"], "")
        
    def test_should_return_404_if_term_not_found(self):
        response = self.client.get(reverse("term_api", kwargs={ "term_key": "foo"}))
        self.assertEqual(response.status_code, 404)
"""
View test cases
"""        
class EditVariableViewTest(MongoTestCase):
    def setUp(self):
        self.v1 = Variable(key=u"Folk10", description=u"Antal bemannade serviceställen", type="integer", is_public=True, target_groups=["public"])
        self.v1.save()
        
        self.new_category = u"Organisation"
        self.new_sub_category = u"Bemannade serviceställen"
        self.new_type = u"string"
        self.new_target_groups = [u"research"]
        self.new_description = u"Summering"
        self.new_comment = u"Inga kommentarer"
        
        self.url = reverse("edit_variable", kwargs={"variable_id":str(self.v1.id)})
        self.client.login(username="admin", password="admin")

    def test_should_update_variable(self):
        response = self.client.post(self.url, {u"category": self.new_category, u"sub_category": self.new_sub_category, 
                               u"type": self.new_type, u"target_groups": self.new_target_groups, u"description": self.new_description, 
                               u"comment": self.new_comment})
        self.assertEquals(response.status_code,200)
        data = json.loads(response.content)
        self.assertFalse('errors' in data)
        
        result = Variable.objects.get(pk=self.v1.id)
        self.assertEquals(result.key, u"Folk10")
        self.assertEquals(result.category, self.new_category)
        self.assertEquals(result.sub_category, self.new_sub_category)
        self.assertEquals(result.type, self.new_type)
        self.assertFalse(result.is_public)
        self.assertEquals(result.target_groups, self.new_target_groups)
        self.assertEquals(result.description, self.new_description)
        self.assertEquals(result.comment, self.new_comment)
    
    def test_should_return_validation_errors_when_omitting_mandatory_fields(self):
        response = self.client.post(self.url, {})
        self.assertEquals(response.status_code,200)
        
        data = json.loads(response.content)
        self.assertTrue(len(data['errors']) == 3)
        self.assertEquals(data['errors'][u'type'], [u'Detta fält måste fyllas i.'])
        self.assertEquals(data['errors'][u'target_groups'], [u'Detta fält måste fyllas i.'])
        self.assertEquals(data['errors'][u'description'], [u'Detta fält måste fyllas i.'])
        
    def test_variable_key_should_not_be_editable(self):
        response = self.client.post(self.url, {u"key": u"TheNewKey", u"type": self.new_type, u"target_groups": self.new_target_groups, u"description": self.new_description})
        self.assertEquals(response.status_code,200)
        result = Variable.objects.get(pk=self.v1.id)
        self.assertEquals(result.key, u"Folk10")
        
    # TODO: Borde man kunna ändra synlighet? Inte om det redan finns publik data eller inlämnade enkätsvar väl? Kommer kräva ompublicering av alla enkätsvar som har variabeln...
    
    # TODO: Borde man kunna ta bort en målgrupp? Samma som ovan.
    
    # TODO: Borde man kunna ändra enhet? Samma som ovan.
        
        
class SurveyResponsesViewTest(MongoTestCase):
    def setUp(self):
        self.survey_response = SurveyResponse(library_name="KARLSTAD STADSBIBLIOTEK", sample_year=2013, target_group="public", observations=[])
        self.survey_response.save()
        sr2 = SurveyResponse(library_name="NORRBOTTENS LÄNSBIBLIOTEK", sample_year=2012, target_group="public", observations=[]);
        sr2.save()
        sr3 = SurveyResponse(library_name="Sjukhusbiblioteken i Dalarnas län", sample_year=2013, target_group="hospital", observations=[]);
        sr3.save()
        
        self.client.login(username="admin", password="admin")
    
    def test_should_not_fetch_survey_responses_unless_list_action_provided(self):
        response = self.client.get(reverse("survey_responses"))
        self.assertEquals(len(response.context["survey_responses"]), 0)
        
    def test_should_list_survey_responses_by_year(self):
        response = self.client.get("{}?action=list&sample_year=2012".format(reverse("survey_responses")))
        self.assertEquals(len(response.context["survey_responses"]), 1)
    
    def test_should_list_survey_responses_by_target_group(self):
        response = self.client.get("{}?action=list&target_group=public".format(reverse("survey_responses")))
        self.assertEquals(len(response.context["survey_responses"]), 2)
    
    def test_should_list_survey_responses_by_year_and_target_group(self):
        response = self.client.get("{}?action=list&target_group=public&sample_year=2013".format(reverse("survey_responses")))
        self.assertEquals(len(response.context["survey_responses"]), 1)
        self.assertEquals(response.context["survey_responses"][0].library_name, "KARLSTAD STADSBIBLIOTEK")
        
    def test_each_survey_response_should_have_checkbox_for_actions(self):
        response = self.client.get("{}?action=list&target_group=public&sample_year=2013".format(reverse("survey_responses")))
        self.assertContains(response, u'<input title="Välj" class="select-one" name="survey-response-ids" type="checkbox" value="{}"/>'.format(self.survey_response.id), 
                            count=1, status_code=200, html=True)
        
    def test_each_survey_response_should_have_a_link_to_details_view(self):
        response = self.client.get("{}?action=list&target_group=public&sample_year=2013".format(reverse("survey_responses")))
        self.assertContains(response, u'<a href="{}" title="Visa/redigera enkätsvar">Visa/redigera</a>'
                            .format(reverse("edit_survey_response", kwargs={"survey_response_id":str(self.survey_response.id)})), 
                            count=1, status_code=200, html=True)
        
class EditSurveyResponseViewTest(MongoTestCase):
    def setUp(self):
#         v1 = Variable(key=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", type="integer", is_public=True, target_groups=["public"])
#         v1.save()
#         v2 = Variable(key=u"folk6", description=u"Är huvudbiblioteket i er kommun integrerat med ett skolbibliotek? 1=ja", type="boolean", is_public=True, target_groups=["public"])
#         v2.save()
#         v3 = Variable(key=u"folk8", description=u"Textkommentar", type="string", is_public=False, target_groups=["public"])
#         v3.save()
        self.survey_response = SurveyResponse(library_name="KARLSTAD STADSBIBLIOTEK", sample_year=2013, target_group="public", observations=[])
#         self.survey_response.observations.append(SurveyObservation(variable=v1, value=7, _source_key="folk5", _is_public=v1.is_public))
#         self.survey_response.observations.append(SurveyObservation(variable=v2, value=None, _source_key="folk6", _is_public=v2.is_public))
#         self.survey_response.observations.append(SurveyObservation(variable=v3, value=u"Här är en kommentar", _source_key="folk8", _is_public=v3.is_public))
        self.survey_response.save()
        
        sr2 = SurveyResponse(library_name="ALE BIBLIOTEK", sample_year=2013, target_group="public", observations=[])
        sr2.save()
        
        self.url = reverse("edit_survey_response", kwargs={"survey_response_id":str(self.survey_response.id)})
        self.client.login(username="admin", password="admin")
        
    def test_view_requires_superuser_login(self):
        # TODO:
        pass
    
    def test_should_have_hidden_inputs_for_mandatory_fields_that_are_not_editable(self):
        response = self.client.get(reverse("edit_survey_response", kwargs={"survey_response_id":str(self.survey_response.id)}))
        self.assertContains(response, u'<input type="hidden" value="2013" name="sample_year" id="id_sample_year">'
                            .format(self.url), count=1, status_code=200, html=True)
        self.assertContains(response, u'<input type="hidden" value="public" name="target_group" id="id_target_group">'
                            .format(self.url), count=1, status_code=200, html=True)
        
    def test_should_update_survey_response(self):
        response = self.client.post(self.url, {u"sample_year": u"2013", u"target_group": u"public", u"library_name": u"Karlstad Stadsbibliotek",
                                               u"municipality_name": u"Karlstads kommun", u"municipality_code": u"1780", 
                                               u"respondent_name": u"Åsa Hansen", u"respondent_email": u"asa.hansen@karlstad.se", u"respondent_phone": u"054-540 23 72"},
                                    follow=True)
        self.assertEquals(response.status_code,200)
        result = SurveyResponse.objects.get(pk=self.survey_response.id)
        self.assertEquals(result.sample_year, 2013)
        self.assertEquals(result.target_group, u"public")
        self.assertEquals(result.library_name, u"Karlstad Stadsbibliotek")
        self.assertEquals(result.metadata.municipality_name, u"Karlstads kommun")
        self.assertEquals(result.metadata.municipality_code, u"1780")
        self.assertEquals(result.metadata.respondent_name, u"Åsa Hansen")
        self.assertEquals(result.metadata.respondent_email, u"asa.hansen@karlstad.se")
        self.assertEquals(result.metadata.respondent_phone, u"054-540 23 72")
        
    def test_should_not_update_sample_year_or_target_group_for_existing_SurveyResponse(self):
        response = self.client.post(self.url, {u"sample_year": u"2014", u"target_group": u"research", u"library_name": u"Karlstad Stadsbibliotek",
                                               u"municipality_name": u"Karlstads kommun", u"municipality_code": u"1780", 
                                               u"respondent_name": u"Åsa Hansen", u"respondent_email": u"asa.hansen@karlstad.se", u"respondent_phone": u"054-540 23 72"}, 
                                    follow=True)
        self.assertEquals(response.status_code, 200)
        result = SurveyResponse.objects.get(pk=self.survey_response.id)
        self.assertEquals(result.sample_year, 2013)
        self.assertEquals(result.target_group, u"public")
        
    def test_should_handle_non_unique_library_name(self):
        response = self.client.post(self.url, {u"sample_year": u"2013", u"target_group": u"public", u"library_name": u"ALE BIBLIOTEK",
                                               u"municipality_name": u"Karlstads kommun", u"municipality_code": u"1780", 
                                               u"respondent_name": u"Åsa Hansen", u"respondent_email": u"asa.hansen@karlstad.se", u"respondent_phone": u"054-540 23 72"},
                                    follow=True)
        
        self.assertEquals(response.context['form']._errors['library_name'], [u"Det finns redan ett enkätsvar för detta bibliotek"])
        
    

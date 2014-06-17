# -*- coding: UTF-8 -*-
from django.test.simple import DjangoTestSuiteRunner
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.management import call_command

from datetime import datetime
import json

from libstat.models import Variable, OpenData, SurveyResponse, SurveyObservation, Library
from libstat.utils import parse_datetime_from_isodate_str

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
        folk52 = Variable.objects.filter(key="Folk52")[0] # Public, type "Procent"
        folk54 = Variable.objects.filter(key="Folk54")[0] # Public, type "Decimal ett"
        folk201 = Variable.objects.filter(key="Folk201")[0] # Private, type "Integer", last row
        
        #  Check visibility
        self.assertFalse(folk1.is_public)
        self.assertFalse(folk7.is_public)
        self.assertTrue(folk8.is_public)
        self.assertTrue(folk26.is_public)
        self.assertTrue(folk52.is_public)
        self.assertTrue(folk54.is_public)
        self.assertFalse(folk201.is_public)
        
        # Check types
        self.assertEquals(folk1.type, u"string")
        self.assertEquals(folk7.type, u"string")
        self.assertEquals(folk8.type, u"boolean")
        self.assertEquals(folk26.type, u"decimal")
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
        forsk154 = Variable.objects.filter(key="Forsk154")[0] # Public, type "Decimal ett"
        
        # Check visibility
        self.assertEquals(forsk1.is_public, False)
        self.assertEquals(forsk2.is_public, False)
        self.assertEquals(forsk8.is_public, True)
        self.assertEquals(forsk154.is_public, True)
        
        # Check types
        self.assertEquals(forsk1.type, u"string")
        self.assertEquals(forsk2.type, u"integer")
        self.assertEquals(forsk8.type, u"decimal")
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
            u"targetGroup": u"public",
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
            u"targetGroup": u"public",
            # u"targetGroup": {u"@id": u"public"}, #TODO
            u"published": "2014-06-03T15:28:31.000000Z",
            u"modified": "2014-06-03T15:28:31.000000Z" 
       }
       self.assertEquals(object.to_dict(), openDataAsDict)
       
       
class VariableTest(MongoTestCase):
    def setUp(self):
        v = Variable(key=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", type="integer", is_public=True, target_groups=["public"])
        v.save()
    
    def test_should_transform_object_to_dict(self):
        object = Variable.objects.first()
        expectedVariableDict = {
            u"@id": u"#folk5",
            u"@type": u"qb:MeasureProperty",
            u"comment": u"Antal bemannade serviceställen, sammanräknat",
            u"range": u"xsd:integer"
        }
        self.assertEqual(object.to_dict(), expectedVariableDict)
    
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
        self.assertEqual(data[u"@context"][u"@vocab"], u"{}/def/terms#".format(settings.API_BASE_URL)),
        self.assertEquals(data[u"@context"][u"@base"], u"{}/data/".format(settings.API_BASE_URL))
        self.assertEqual(data[u"@context"][u"observations"], u"@graph")
    
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
        self.assertEqual(data[u"@context"][u"@vocab"], u"{}/def/terms#".format(settings.API_BASE_URL)),
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
        self.assertEqual(data[u"@context"][u"xsd"], u"http://www.w3.org/2001/XMLSchema#")
        self.assertEqual(data[u"@context"][u"rdfs"], u"http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.assertEqual(data[u"@context"][u"rdf"], u"http://www.w3.org/2000/01/rdf-schema#")
        self.assertEqual(data[u"@context"][u"foaf"], u"http://xmlns.com/foaf/0.1/")
        self.assertEqual(data[u"@context"][u"qb"], u"http://purl.org/linked-data/cube#")
        self.assertEqual(data[u"@context"][u"terms"], u"@graph")
        self.assertEqual(data[u"@context"][u"@language"], u"sv")
        self.assertEqual(data[u"@context"][u"label"], u"rdfs:label")
        self.assertEqual(data[u"@context"][u"range"], {u"@id": u"rdfs:range", u"@type": u"@id"})
        self.assertEqual(data[u"@context"][u"comment"], u"rdfs:comment")
        self.assertEqual(data[u"@context"][u"subClassOf"], {u"@id": u"rdfs:subClassOf", u"@type": u"@id"})
        self.assertEqual(data[u"@context"][u"name"], u"foaf:name")
        
    def test_should_contain_hardcoded_terms(self):
        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)
        ids = [term[u"@id"] for term in data[u"terms"]]
        self.assertTrue(u"#library" in ids)
        self.assertTrue(u"#sampleYear" in ids)
        self.assertTrue(u"#targetGroup" in ids)
        self.assertTrue(u"#modified" in ids)
        self.assertTrue(u"#published" in ids)
        self.assertTrue(u"#Observation" in ids)
    
    def test_should_return_all_variables(self):
        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)
        ids = [term[u"@id"] for term in data[u"terms"]]
        self.assertTrue(u"#folk5" in ids)
        
        
class TermApiTest(MongoTestCase):
    def setUp(self):
        v1 = Variable(key=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", type="integer", is_public=True, target_groups=["public"])
        v1.save()
    
    def test_response_should_return_jsonld(self):
        response = self.client.get(reverse("term_api", kwargs={ "term_key": "folk5"}))
        self.assertEqual(response["Content-Type"], "application/ld+json")
        
    def test_response_should_contain_context(self):
        response = self.client.get(reverse("term_api", kwargs={ "term_key": "folk5"}))
        data = json.loads(response.content)
        self.assertEqual(data[u"@context"][u"xsd"], u"http://www.w3.org/2001/XMLSchema#")
        self.assertEqual(data[u"@context"][u"rdfs"], u"http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.assertEqual(data[u"@context"][u"rdf"], u"http://www.w3.org/2000/01/rdf-schema#")
        self.assertEqual(data[u"@context"][u"qb"], u"http://purl.org/linked-data/cube#")
        self.assertEqual(data[u"@context"][u"@language"], u"sv")
        self.assertEqual(data[u"@context"][u"label"], u"rdfs:label")
        self.assertEqual(data[u"@context"][u"range"], {u"@id": u"rdfs:range", u"@type": u"@id"})
        self.assertEqual(data[u"@context"][u"comment"], u"rdfs:comment")
        self.assertEqual(data[u"@context"][u"subClassOf"], {u"@id": u"rdfs:subClassOf", u"@type": u"@id"})  
        
    def test_should_return_one_term(self):
        response = self.client.get(reverse("term_api", kwargs={ "term_key": "folk5"}))
        data = json.loads(response.content)
        self.assertEquals(data[u"@id"], u"folk5"),
        self.assertEquals(data[u"@type"], u"qb:MeasureProperty"),
        self.assertEquals(data[u"comment"], u"Antal bemannade serviceställen, sammanräknat"),
        self.assertEquals(data[u"range"], u"xsd:integer")
        
    def test_should_return_404_if_term_not_found(self):
        response = self.client.get(reverse("term_api", kwargs={ "term_key": "foo"}))
        self.assertEqual(response.status_code, 404)
    
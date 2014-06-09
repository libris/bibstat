# -*- coding: UTF-8 -*-
from django.test.simple import DjangoTestSuiteRunner
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse

from datetime import datetime
import json

from libstat.models import Variable, OpenData, SurveyResponse, SurveyObservation

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
    Model class test cases
"""
class SurveyResponseTest(MongoTestCase):
    def setUp(self):
        v1 = Variable(key=u"folk5", alias=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", is_public=True, type="xsd:integer", target_groups=["public"])
        v1.save()
        v2 = Variable(key=u"folk6", alias=u"folk6", description=u"Är huvudbiblioteket i er kommun integrerat med ett skolbibliotek? 1=ja", is_public=True, type="xsd:integer", target_groups=["public"])
        v2.save()
        v3 = Variable(key=u"folk8", alias=u"folk8", description=u"Textkommentar", is_public=False, type="xsd:string", target_groups=["public"])
        v3.save()
        sr = SurveyResponse(library="Kld1", sample_year=2013, target_group="public", observations=[])
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
        self.assertEquals(open_data.library, "Kld1")
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
        self.assertEquals(open_data.library, "Kld1")
        self.assertEquals(open_data.sample_year, 2013)
        self.assertEquals(open_data.variable.key, "folk5")
        self.assertEquals(open_data.target_group, "public")
        self.assertEquals(open_data.value, 9)
        self.assertTrue(open_data.date_modified)
        self.assertTrue(open_data.date_created)
        self.assertNotEquals(open_data.date_created, open_data.date_modified)
        
    
class OpenDataTest(MongoTestCase):
    def setUp(self):
        v = Variable(key=u"folk5", alias=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", is_public=True, type="xsd:integer", target_groups=["public"])
        v.save()
        publishing_date = datetime(2014, 06, 03, 15, 28, 31)
        d = OpenData(library="Kld1", sample_year=2013, target_group="public", variable=v, value=6, date_created=publishing_date, date_modified=publishing_date)
        d.save()
        
    def test_should_transform_object_to_dict(self):
       object = OpenData.objects.first()
       openDataAsDict = {
            u"@id": str(object.id),
            u"@type": u"Observation",
            u"folk5": 6, 
            u"library": {u"@id": u"{}/library/Kld1".format(settings.BIBDB_BASE_URL)},
            u"sampleYear": 2013,
            u"targetGroup": u"public",
            # u"targetGroup": {u"@id": u"public"}, #TODO
            u"published": "2014-06-03T15:28:31Z",
            u"modified": "2014-06-03T15:28:31Z" 
       }
       self.assertEquals(object.to_dict(), openDataAsDict)
       
       
class VariableTest(MongoTestCase):
    def setUp(self):
        v = Variable(key=u"folk5", alias=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", is_public=True, type="xsd:integer", target_groups=["public"])
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
        v1 = Variable(key=u"folk5", alias=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", is_public=True, type="xsd:integer", target_groups=["public"])
        v1.save()
        v2 = Variable(key=u"folk6", alias=u"folk6", description=u"Är huvudbiblioteket i er kommun integrerat med ett skolbibliotek? 1=ja", is_public=True, type="xsd:integer", target_groups=["public"])
        v2.save()
        
        creation_date = datetime(2014, 05, 27, 8, 00, 00)
        date1 = datetime(2014, 06, 02, 17, 57, 16)
        d1 = OpenData(library="Lu", sample_year=2013, target_group="public", variable=v1, value=7, date_created=creation_date, date_modified=date1)
        d1.save()
        
        date1 = datetime(2014, 06, 03, 15, 28, 31)
        d1 = OpenData(library="Kld1", sample_year=2013, target_group="public", variable=v1, value=6, date_created=creation_date, date_modified=date1)
        d1.save()
        
        date2 = datetime(2014, 06, 04, 11, 14, 01)
        d2 = OpenData(library="Ga", sample_year=2013, target_group="public", variable=v2, value=1, date_created=creation_date, date_modified=date2)
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
        self.assertEquals(data[u"observations"][0][u"library"][u"@id"], u"{}/library/Ga".format(settings.BIBDB_BASE_URL))
    
    def test_should_filter_data_by_to_date(self):
        response = self.client.get(u"{}?to_date=2014-06-03".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"][u"@id"], u"{}/library/Lu".format(settings.BIBDB_BASE_URL))
        
    def test_should_filter_data_by_date_range(self):
        response = self.client.get(u"{}?from_date=2014-06-03&to_date=2014-06-04".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"][u"@id"], u"{}/library/Kld1".format(settings.BIBDB_BASE_URL))
    
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

        
class TermsApiTest(MongoTestCase):
    def setUp(self):
        v = Variable(key=u"folk5", alias=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", is_public=True, type="xsd:integer", target_groups=["public"])
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
        self.assertEqual(data[u"@context"][u"qb"], u"http://purl.org/linked-data/cube#")
        self.assertEqual(data[u"@context"][u"terms"], u"@graph")
        self.assertEqual(data[u"@context"][u"@language"], u"sv")
        self.assertEqual(data[u"@context"][u"label"], u"rdfs:label")
        self.assertEqual(data[u"@context"][u"range"], {u"@id": u"rdfs:range", u"@type": u"@id"})
        self.assertEqual(data[u"@context"][u"comment"], u"rdfs:comment")
        self.assertEqual(data[u"@context"][u"subClassOf"], {u"@id": u"rdfs:subClassOf", u"@type": u"@id"})
        
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
    
# -*- coding: UTF-8 -*-
from libstat.tests import MongoTestCase
from django.core.urlresolvers import reverse
import json
from datetime import datetime

from django.conf import settings
from libstat.models import Variable, OpenData
from libstat.apis import data_context, term_context

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
        
        
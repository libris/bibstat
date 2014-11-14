# -*- coding: UTF-8 -*-
import json
from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from django.conf import settings

from libstat.models import Variable
from libstat.tests import MongoTestCase
from libstat.views.apis import data_context, term_context


class OpenDataApiTest(MongoTestCase):

    def test_response_should_return_jsonld(self):
        response = self.client.get(reverse("data_api"))

        self.assertEqual(response["Content-Type"], "application/ld+json")

    def test_response_should_contain_context(self):
        response = self.client.get(reverse("data_api"))
        data = json.loads(response.content)

        self.assertEquals(data[u"@context"], data_context)

    def test_should_not_filter_by_date_unless_requested(self):
        self._dummy_open_data(library_id="1")
        self._dummy_open_data(library_id="2")
        self._dummy_open_data(library_id="3")

        response = self.client.get(reverse("data_api"))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 3)

    def test_should_filter_data_by_from_date(self):
        self._dummy_open_data(library_id="11070", date_modified=datetime(2014, 06, 05, 11, 14, 01))

        response = self.client.get(u"{}?from_date=2014-06-04".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"][u"@id"],
                          u"{}/library/11070".format(settings.BIBDB_BASE_URL))

    def test_should_filter_data_by_to_date(self):
        self._dummy_open_data(library_id="81", date_modified=datetime(2014, 06, 02, 11, 14, 01))

        response = self.client.get(u"{}?to_date=2014-06-03".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"][u"@id"],
                          u"{}/library/81".format(settings.BIBDB_BASE_URL))

    def test_should_filter_data_by_date_range(self):
        self._dummy_open_data(library_id="323", date_modified=datetime(2014, 06, 03, 11, 14, 01))

        response = self.client.get(
            u"{}?from_date=2014-06-02T15:28:31.000&to_date=2014-06-04T11:14:00.000".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"][u"@id"],
                          u"{}/library/323".format(settings.BIBDB_BASE_URL))

    def test_should_limit_results(self):
        self._dummy_open_data(library_id="1")
        self._dummy_open_data(library_id="2")
        self._dummy_open_data(library_id="3")

        response = self.client.get(u"{}?limit=2".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 2)

    def test_should_limit_results_with_offset(self):
        self._dummy_open_data(library_id="1")
        self._dummy_open_data(library_id="2")
        self._dummy_open_data(library_id="3")

        response = self.client.get(u"{}?limit=2&offset=2".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)

    def test_should_filter_by_term_key(self):
        variable = self._dummy_variable(key=u"folk6")
        self._dummy_open_data(variable=variable)

        response = self.client.get(u"{}?term=folk6".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"folk6"], 1)

    def test_should_return_empty_result_if_unknown_term(self):
        response = self.client.get(u"{}?term=hej".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 0)


class ObservationApiTest(MongoTestCase):

    def test_response_should_return_jsonld(self):
        obs = self._dummy_open_data()

        response = self.client.get(reverse("observation_api", kwargs={"observation_id": str(obs.id)}))

        self.assertEqual(response["Content-Type"], "application/ld+json")

    def test_response_should_contain_context(self):
        obs = self._dummy_open_data()

        response = self.client.get(reverse("observation_api", kwargs={"observation_id": str(obs.id)}))
        data = json.loads(response.content)

        self.assertEqual(data[u"@context"][u"@vocab"], u"{}/def/terms/".format(settings.API_BASE_URL)),
        self.assertEquals(data[u"@context"][u"@base"], u"{}/data/".format(settings.API_BASE_URL))

    def test_should_return_one_observation(self):
        variable = self._dummy_variable(key=u"folk5")
        obs = self._dummy_open_data(variable=variable, sample_year=2013)

        response = self.client.get(reverse("observation_api", kwargs={"observation_id": str(obs.id)}))
        data = json.loads(response.content)

        self.assertEqual(data[u"@id"], str(obs.id))
        self.assertEqual(data[u"@type"], u"Observation")
        self.assertEqual(data[u"folk5"], obs.value)
        self.assertEqual(data[u"library"], {u"@id": u"{}/library/{}".format(settings.BIBDB_BASE_URL, obs.library_id)})
        self.assertEqual(data[u"sampleYear"], obs.sample_year)
        self.assertEqual(data[u"published"], obs.date_created_str())
        self.assertEqual(data[u"modified"], obs.date_modified_str())

    def test_should_return_404_if_observation_not_found(self):
        response = self.client.get(reverse("observation_api", kwargs={"observation_id": "12323873982375a8c0g"}))

        self.assertEqual(response.status_code, 404)


class TermsApiTest(MongoTestCase):

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
        self._dummy_variable(key=u"folk5")

        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)
        ids = [term[u"@id"] for term in data[u"terms"]]

        self.assertTrue(u"folk5" in ids)

    def test_should_not_return_variable_drafts(self):
        self._dummy_variable(key=u"69", is_draft=True)

        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)
        ids = [term[u"@id"] for term in data[u"terms"]]

        self.assertFalse(u"Folk69" in ids)


class TermApiTest(MongoTestCase):

    def test_response_should_return_jsonld(self):
        self._dummy_variable(key=u"folk5")

        response = self.client.get(reverse("term_api", kwargs={"term_key": "folk5"}))

        self.assertEqual(response["Content-Type"], "application/ld+json")

    def test_response_should_contain_context(self):
        self._dummy_variable(key=u"folk5")

        response = self.client.get(reverse("term_api", kwargs={"term_key": "folk5"}))
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
        self.assertEqual(data[u"@context"][u"replaces"], {u"@id": u"dcterms:replaces", u"@type": u"@id"})
        self.assertEqual(data[u"@context"][u"replacedBy"], {u"@id": u"dcterms:isReplacedBy", u"@type": u"@id"})
        self.assertEqual(data[u"@context"][u"valid"], {u"@id": u"dcterms:valid", u"@type": u"dcterms:Period"})

    def test_should_return_one_term(self):
        self._dummy_variable(key=u"folk5", description=u"some description", type="integer")

        response = self.client.get(reverse("term_api", kwargs={"term_key": "folk5"}))
        data = json.loads(response.content)

        self.assertEquals(len(data), 6)
        self.assertEquals(data[u"@context"], term_context)
        self.assertEquals(data[u"@id"], u"folk5"),
        self.assertEquals(data[u"@type"], [u"rdf:Property", u"qb:MeasureProperty"]),
        self.assertEquals(data[u"comment"], u"some description"),
        self.assertEquals(data[u"range"], u"xsd:integer")
        self.assertEquals(data[u"isDefinedBy"], "")

    def test_should_return_404_if_term_not_found(self):
        response = self.client.get(reverse("term_api", kwargs={"term_key": "foo"}))
        self.assertEqual(response.status_code, 404)

    def test_should_return_404_if_term_is_draft(self):
        response = self.client.get(reverse("term_api", kwargs={"term_key": "Folk69"}))
        self.assertEqual(response.status_code, 404)


class ReplaceableVariablesApiTest(MongoTestCase):

    def setUp(self):
        self.url = reverse("replaceable_variables_api")
        self.client.login(username="admin", password="admin")

    def test_view_requires_admin_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.login(username="library_user", password="secret")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.logout()
        self.client.login(username="admin", password="admin")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_should_return_replaceable_variables_as_json(self):
        var1 = self._dummy_variable(key=u"key_1")
        self._dummy_variable(key=u"key_2", is_draft=True)
        self._dummy_variable(key=u"key_3", replaced_by=var1)
        var4 = self._dummy_variable(key=u"key_4")

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, [{"key": "key_1",
                                  "id": str(var1.id),
                                  "description": var1.description},
                                 {"key": "key_4",
                                  "id": str(var4.id),
                                  "description": var4.description}])

    def test_should_filter_replaceables_by_key(self):
        var = self._dummy_variable(key=u"Folk28")

        response = self.client.get("{}?q=fo".format(self.url))
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, [{"key": "Folk28",
                                  "id": str(var.id),
                                  "description": var.description}])

    def test_should_filter_replaceables_by_description(self):
        var = self._dummy_variable(key=u"Skol10", description=u"Postort", type="string")
        response = self.client.get("{}?q=post".format(self.url))
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, [{"key": "Skol10",
                                  "id": str(var.id),
                                  "description": var.description}])

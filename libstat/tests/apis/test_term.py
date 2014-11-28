# -*- coding: UTF-8 -*-
import json

from django.core.urlresolvers import reverse

from libstat.tests import MongoTestCase
from libstat.apis.terms import term_context


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

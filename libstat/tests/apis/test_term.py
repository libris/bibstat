import json

from django.urls import reverse

from libstat.tests import MongoTestCase
from libstat.apis.terms import term_context


class TermApiTest(MongoTestCase):
    def test_response_should_return_jsonld(self):
        self._dummy_variable(key="folk5")

        response = self.client.get(reverse("term_api", kwargs={"term_key": "folk5"}))

        self.assertEqual(response["Content-Type"], "application/ld+json")

    def test_response_should_contain_context(self):
        self._dummy_variable(key="folk5")

        response = self.client.get(reverse("term_api", kwargs={"term_key": "folk5"}))
        data = json.loads(response.content)

        self.assertEqual(data["@context"]["xsd"], "http://www.w3.org/2001/XMLSchema#")
        self.assertEqual(data["@context"]["rdf"], "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.assertEqual(data["@context"]["rdfs"], "http://www.w3.org/2000/01/rdf-schema#")
        self.assertEqual(data["@context"]["qb"], "http://purl.org/linked-data/cube#")
        self.assertEqual(data["@context"]["@language"], "sv")
        self.assertEqual(data["@context"]["label"], "rdfs:label")
        self.assertEqual(data["@context"]["range"], {"@id": "rdfs:range", "@type": "@id"})
        self.assertEqual(data["@context"]["comment"], "rdfs:comment")
        self.assertEqual(data["@context"]["subClassOf"], {"@id": "rdfs:subClassOf", "@type": "@id"})
        self.assertEqual(data["@context"]["replaces"], {"@id": "dcterms:replaces", "@type": "@id"})
        self.assertEqual(data["@context"]["replacedBy"], {"@id": "dcterms:isReplacedBy", "@type": "@id"})
        self.assertEqual(data["@context"]["valid"], {"@id": "dcterms:valid", "@type": "dcterms:Period"})

    def test_should_return_one_term(self):
        self._dummy_variable(key="folk5", description="some description", type="integer")

        response = self.client.get(reverse("term_api", kwargs={"term_key": "folk5"}))
        data = json.loads(response.content)

        self.assertEqual(len(data), 6)
        self.assertEqual(data["@context"], term_context)
        self.assertEqual(data["@id"], "folk5"),
        self.assertEqual(data["@type"], ["rdf:Property", "qb:MeasureProperty"]),
        self.assertEqual(data["comment"], "some description"),
        self.assertEqual(data["range"], "xsd:integer")
        self.assertEqual(data["isDefinedBy"], "")

    def test_should_return_404_if_term_not_found(self):
        response = self.client.get(reverse("term_api", kwargs={"term_key": "foo"}))
        self.assertEqual(response.status_code, 404)

    def test_should_return_404_if_term_is_draft(self):
        response = self.client.get(reverse("term_api", kwargs={"term_key": "Folk69"}))
        self.assertEqual(response.status_code, 404)

# -*- coding: UTF-8 -*-
import json

from django.urls import reverse

from libstat.tests import MongoTestCase
from libstat.apis.terms import term_context


class TermsApiTest(MongoTestCase):

    def test_response_should_return_jsonld(self):
        response = self.client.get(reverse("terms_api"))

        self.assertEqual(response["Content-Type"], "application/ld+json")

    def test_response_should_contain_context(self):
        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)

        self.assertEqual(data["@context"], term_context)

    def test_should_contain_hardcoded_terms(self):
        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)
        ids = [term["@id"] for term in data["terms"]]

        self.assertTrue("library" in ids)
        self.assertTrue("sampleYear" in ids)
        self.assertTrue("targetGroup" in ids)
        self.assertTrue("modified" in ids)
        self.assertTrue("published" in ids)
        self.assertTrue("Observation" in ids)

    def test_should_return_all_variables(self):
        self._dummy_variable(key="folk5")

        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)
        ids = [term["@id"] for term in data["terms"]]

        self.assertTrue("folk5" in ids)

    def test_should_not_return_variable_drafts(self):
        self._dummy_variable(key="69", is_draft=True)

        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)
        ids = [term["@id"] for term in data["terms"]]

        self.assertFalse("Folk69" in ids)

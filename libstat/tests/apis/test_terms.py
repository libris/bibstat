# -*- coding: UTF-8 -*-
import json

from django.core.urlresolvers import reverse

from libstat.tests import MongoTestCase
from libstat.views.apis import term_context


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



# -*- coding: UTF-8 -*-
import json
from datetime import datetime

from django.core.urlresolvers import reverse
from django.conf import settings

from libstat.tests import MongoTestCase
from libstat.apis.open_data import data_context


class OpenDataApiTest(MongoTestCase):

    def test_response_should_return_jsonld(self):
        response = self.client.get(reverse("data_api"))

        self.assertEqual(response["Content-Type"], "application/ld+json")

    def test_response_should_contain_context(self):
        response = self.client.get(reverse("data_api"))
        data = json.loads(response.content)

        self.assertEquals(data[u"@context"], data_context)

    def test_should_not_filter_by_date_unless_requested(self):
        self._dummy_open_data()
        self._dummy_open_data()
        self._dummy_open_data()

        response = self.client.get(reverse("data_api"))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 3)

    def test_should_filter_data_by_from_date(self):
        self._dummy_open_data(sigel="sigel_1", date_modified=datetime(2014, 06, 05, 11, 14, 01))

        response = self.client.get(u"{}?from_date=2014-06-04".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"][u"@id"],
                          u"{}/library/sigel_1".format(settings.BIBDB_BASE_URL))

    def test_should_filter_data_by_to_date(self):
        self._dummy_open_data(sigel="81", date_modified=datetime(2014, 06, 02, 11, 14, 01))

        response = self.client.get(u"{}?to_date=2014-06-03".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"][u"@id"],
                          u"{}/library/81".format(settings.BIBDB_BASE_URL))

    def test_should_filter_data_by_date_range(self):
        self._dummy_open_data(sigel="323", date_modified=datetime(2014, 06, 03, 11, 14, 01))

        response = self.client.get(
            u"{}?from_date=2014-06-02T15:28:31.000&to_date=2014-06-04T11:14:00.000".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"][u"@id"],
                          u"{}/library/323".format(settings.BIBDB_BASE_URL))

    def test_should_limit_results(self):
        self._dummy_open_data()
        self._dummy_open_data()
        self._dummy_open_data()

        response = self.client.get(u"{}?limit=2".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 2)

    def test_should_limit_results_with_offset(self):
        self._dummy_open_data()
        self._dummy_open_data()
        self._dummy_open_data()

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

    def test_should_filter_by_sigel(self):
        variable = self._dummy_variable(key=u"folk6")
        self._dummy_open_data(variable=variable, sigel="testsigel")

        response = self.client.get(u"{}?term=folk6&sigel=testsigel".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"folk6"], 1)

    def should_return_empty_result_if_unknown_sigel(self):
        response = self.client.get(u"{}?term=folk6&sigel=ho".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 0)

    def test_should_filter_by_sample_year(self):
        variable = self._dummy_variable(key=u"folk7")
        self._dummy_open_data(variable=variable, sample_year=2014)

        response = self.client.get(u"{}?term=folk7&sample_year=2014".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"folk7"], 1)

    def should_return_empty_result_if_unknown_sample_year(self):
        response = self.client.get(u"{}?term=folk7&sample_year=2222".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 0)

    def test_should_filter_by_library_type(self):
        variable = self._dummy_variable(key=u"folk8")
        library = self._dummy_library(sigel="testsigel", library_type="folkbib")
        survey = self._dummy_survey(library=library)
        self._dummy_open_data(source_survey=survey, variable=variable, sigel="testsigel")

        response = self.client.get(u"{}?term=folk8&library_type=folkbib".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"folk8"], 1)

    def should_return_empty_result_if_unknown_library_type(self):
        response = self.client.get(u"{}?term=folk8&library_type=hej".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 0)

    def test_should_filter_by_muncipality_code(self):
        variable = self._dummy_variable(key=u"folk9")
        library = self._dummy_library(sigel="testsigel", municipality_code="2281")
        survey = self._dummy_survey(library=library)
        self._dummy_open_data(source_survey=survey, variable=variable, sigel="testsigel")

        response = self.client.get(u"{}?term=folk9&municipality_code=2281".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"folk9"], 1)

    def should_return_empty_result_if_unknown_municipality_code(self):
        response = self.client.get(u"{}?term=folk9&municipality_code=hej".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 0)

    def test_should_only_return_active_open_data_entries(self):
        self._dummy_open_data(is_active=True)
        self._dummy_open_data(is_active=False)

        response = self._get_json("data_api")

        self.assertEquals(len(response[u"observations"]), 1)

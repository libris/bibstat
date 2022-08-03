import json
from datetime import datetime

from django.urls import reverse
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

        self.assertEqual(data["@context"], data_context)

    def test_should_not_filter_by_date_unless_requested(self):
        self._dummy_open_data()
        self._dummy_open_data()
        self._dummy_open_data()

        response = self.client.get(reverse("data_api"))
        data = json.loads(response.content)

        self.assertEqual(len(data["observations"]), 3)

    def test_should_filter_data_by_from_date(self):
        self._dummy_open_data(
            sigel="sigel_1", date_modified=datetime(2014, 6, 5, 11, 14, 1)
        )

        response = self.client.get(
            "{}?from_date=2014-06-04".format(reverse("data_api"))
        )
        data = json.loads(response.content)

        self.assertEqual(len(data["observations"]), 1)
        self.assertEqual(
            data["observations"][0]["library"]["@id"],
            "{}/library/sigel_1".format(settings.BIBDB_BASE_URL),
        )

    def test_should_filter_data_by_to_date(self):
        self._dummy_open_data(sigel="81", date_modified=datetime(2014, 6, 2, 11, 14, 1))

        response = self.client.get("{}?to_date=2014-06-03".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEqual(len(data["observations"]), 1)
        self.assertEqual(
            data["observations"][0]["library"]["@id"],
            "{}/library/81".format(settings.BIBDB_BASE_URL),
        )

    def test_should_filter_data_by_date_range(self):
        self._dummy_open_data(
            sigel="323", date_modified=datetime(2014, 6, 3, 11, 14, 1)
        )

        response = self.client.get(
            "{}?from_date=2014-06-02T15:28:31.000&to_date=2014-06-04T11:14:00.000".format(
                reverse("data_api")
            )
        )
        data = json.loads(response.content)

        self.assertEqual(len(data["observations"]), 1)
        self.assertEqual(
            data["observations"][0]["library"]["@id"],
            "{}/library/323".format(settings.BIBDB_BASE_URL),
        )

    def test_should_limit_results(self):
        self._dummy_open_data()
        self._dummy_open_data()
        self._dummy_open_data()

        response = self.client.get("{}?limit=2".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEqual(len(data["observations"]), 2)

    def test_should_limit_results_with_offset(self):
        self._dummy_open_data()
        self._dummy_open_data()
        self._dummy_open_data()

        response = self.client.get("{}?limit=2&offset=2".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEqual(len(data["observations"]), 1)

    def test_should_filter_by_term_key(self):
        variable = self._dummy_variable(key="folk6")
        self._dummy_open_data(variable=variable)

        response = self.client.get("{}?term=folk6".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEqual(len(data["observations"]), 1)
        self.assertEqual(data["observations"][0]["folk6"], 1)

    def test_should_return_empty_result_if_unknown_term(self):
        response = self.client.get("{}?term=hej".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEqual(len(data["observations"]), 0)

    def test_should_only_return_active_open_data_entries(self):
        self._dummy_open_data(is_active=True)
        self._dummy_open_data(is_active=False)

        response = self._get_json("data_api")

        self.assertEqual(len(response["observations"]), 1)

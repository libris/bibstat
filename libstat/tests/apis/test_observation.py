import json

from django.urls import reverse
from django.conf import settings

from libstat.tests import MongoTestCase


class ObservationApiTest(MongoTestCase):
    def test_response_should_return_jsonld(self):
        obs = self._dummy_open_data()

        response = self.client.get(
            reverse("observation_api", kwargs={"observation_id": str(obs.id)})
        )

        self.assertEqual(response["Content-Type"], "application/ld+json")

    def test_response_should_contain_context(self):
        obs = self._dummy_open_data()

        response = self.client.get(
            reverse("observation_api", kwargs={"observation_id": str(obs.id)})
        )
        data = json.loads(response.content)

        self.assertEqual(
            data["@context"]["@vocab"], "{}/def/terms/".format(settings.API_BASE_URL)
        ),
        self.assertEqual(
            data["@context"]["@base"], "{}/data/".format(settings.API_BASE_URL)
        )

    def test_should_return_one_observation(self):
        variable = self._dummy_variable(key="folk5")
        obs = self._dummy_open_data(variable=variable, sample_year=2013)

        response = self.client.get(
            reverse("observation_api", kwargs={"observation_id": str(obs.id)})
        )
        data = json.loads(response.content)

        self.assertEqual(data["@id"], str(obs.id))
        self.assertEqual(data["@type"], "Observation")
        self.assertEqual(data["folk5"], obs.value)
        self.assertEqual(
            data["library"]["@id"],
            "{}/library/{}".format(settings.BIBDB_BASE_URL, obs.sigel),
        )
        self.assertEqual(data["library"]["name"], obs.library_name)
        self.assertEqual(data["sampleYear"], obs.sample_year)
        self.assertEqual(data["published"], obs.date_created_str())
        self.assertEqual(data["modified"], obs.date_modified_str())

    def test_should_return_404_if_observation_not_found(self):
        response = self.client.get(
            reverse("observation_api", kwargs={"observation_id": "12323873982375a8c0g"})
        )

        self.assertEqual(response.status_code, 404)

from libstat.tests import MongoTestCase


class ReportSelectionTest(MongoTestCase):
    def test_can_view_report_selection_if_not_logged_in(self):
        response = self._get("reports")

        self.assertEqual(response.status_code, 200)

    def test_can_view_report_selection_if_logged_in(self):
        self._login()
        response = self._get("reports")

        self.assertEqual(response.status_code, 200)

    def test_can_filter_reports_by_sample_year(self):
        self._dummy_survey(
            sample_year=2014, observations=[self._dummy_observation()]
        ).publish()

        response = self._get("reports", params={"sample_year": "2014", "submit": "1"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["surveys"]), 1)

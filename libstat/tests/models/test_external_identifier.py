from libstat.models import Survey
from libstat.tests import MongoTestCase


class TestExternalIdentifier(MongoTestCase):

    def test_should_save_external_identifier_to_survey_library(self):
        external_identifier = self._dummy_external_identifier(type="school_code", identifier="11111111")
        library = self._dummy_library(sigel="testsigel", external_identifiers=[external_identifier])
        self._dummy_survey(library=library)

        survey = Survey.objects.filter(library__sigel="testsigel").first()

        self.assertEqual(survey.library.external_identifiers[0].type, "school_code")
        self.assertEqual(survey.library.external_identifiers[0].identifier, "11111111")
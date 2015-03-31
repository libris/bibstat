from libstat.tests import MongoTestCase
from libstat.services import clean_data
from libstat.models import Library

class TestCleanDataFunctions(MongoTestCase):

    def test_update_sigel(self):
        random_sigel = Library._random_sigel()
        library = self._dummy_library(sigel=random_sigel)
        survey1 = self._dummy_survey(library=library, observations=[self._dummy_observation()])
        survey2 = self._dummy_survey()
        clean_data._update_sigel(survey1, survey2)
        self.assertEqual(survey1.library.sigel, survey2.library.sigel)
        self.assertTrue(survey1.library.sigel in survey1.selected_libraries)
        self.assertTrue(random_sigel not in survey1.selected_libraries)
        self.assertEqual(survey1._status, u"published")

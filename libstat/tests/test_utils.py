from datetime import datetime

from libstat.tests import MongoTestCase
from libstat.utils import parse_datetime_from_isodate_str


class UtilsTest(MongoTestCase):

    def test_should_parse_datetime_from_isodate_str(self):
        self.assertEquals(parse_datetime_from_isodate_str("2014-06-03T15:47:22.873+02:00"), None)
        self.assertEquals(parse_datetime_from_isodate_str("2014-06-03T15:47:22.873Z"), None)
        self.assertEquals(parse_datetime_from_isodate_str("2014-06-03T15:47:22.873"),
                          datetime(2014, 6, 3, 15, 47, 22, 873000))
        self.assertEquals(parse_datetime_from_isodate_str("2014-06-03T15:47:22"), datetime(2014, 6, 3, 15, 47, 22))
        self.assertEquals(parse_datetime_from_isodate_str("2014-06-03T15:47"), datetime(2014, 6, 3, 15, 47))
        self.assertEquals(parse_datetime_from_isodate_str("2014-06-03T15"), datetime(2014, 6, 3, 15))
        self.assertEquals(parse_datetime_from_isodate_str("2014-06-03"), datetime(2014, 6, 3))
        self.assertEquals(parse_datetime_from_isodate_str("2014-06"), datetime(2014, 6, 1))
        self.assertEquals(parse_datetime_from_isodate_str("2014"), datetime(2014, 1, 1))
        self.assertEquals(parse_datetime_from_isodate_str("jun 3 2014"), None)

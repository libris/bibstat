# -*- coding: UTF-8 -*-
from libstat.tests import MongoTestCase
from libstat.templatetags.libstat_tags import *


class LibstatTagsTest(MongoTestCase):
    def test__tg_label__should_return_string_for_single_target_group(self):
        self.assertEquals(tg_label(u"public"), u"Folkbibliotek")
        self.assertEquals(tg_label(u"research"), u"Forskningsbibliotek")
        self.assertEquals(tg_label(u"hospital"), u"Sjukhusbibliotek")
        self.assertEquals(tg_label(u"school"), u"Skolbibliotek")

    def test__tg_label__should_return_string_for_list_of_target_groups(self):
        self.assertEquals(tg_label([u"public"]), u"Folkbibliotek")
        self.assertEquals(tg_label([u"school", u"hospital"]), u"Skolbibliotek, Sjukhusbibliotek")
        self.assertEquals(tg_label([u"school", u"hospital", u"public"]),
                          u"Skolbibliotek, Sjukhusbibliotek, Folkbibliotek")
        # Use special label if all available target groups is value
        self.assertEquals(tg_label([u"school", u"hospital", u"public", u"research"]), u"Samtliga bibliotekstyper")

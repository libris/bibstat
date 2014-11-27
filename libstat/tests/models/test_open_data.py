# -*- coding: UTF-8 -*-
from datetime import datetime
from bibstat import settings
from libstat.models import Variable
from libstat.models import OpenData
from libstat.tests import MongoTestCase


class OpenDataTest(MongoTestCase):

    def setUp(self):
        v = Variable(key=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", type="integer",
                     is_public=True, target_groups=["folkbib"])
        v.save()
        publishing_date = datetime(2014, 06, 03, 15, 28, 31)
        d1 = OpenData(library_name=u"KARLSTAD STADSBIBLIOTEK", sigel="323", sample_year=2013,
                      target_group="folkbib", variable=v, value=6, date_created=publishing_date,
                      date_modified=publishing_date)
        d1.save()
        d2 = OpenData(library_name=u"NORRBOTTENS LÄNSBIBLIOTEK", sample_year=2013, target_group="folkbib", variable=v,
                      value=6, date_created=publishing_date, date_modified=publishing_date)
        d2.save()

    def test_should_transform_object_with_sigel_to_dict(self):
        object = OpenData.objects.get(library_name=u"KARLSTAD STADSBIBLIOTEK")
        openDataAsDict = {
            u"@id": str(object.id),
            u"@type": u"Observation",
            u"folk5": 6,
            u"library": {
                u"@id": u"{}/library/323".format(settings.BIBDB_BASE_URL),
                u"name": u"KARLSTAD STADSBIBLIOTEK"
            },
            u"sampleYear": 2013,
            u"targetGroup": u"Folkbibliotek",
            # u"targetGroup": {u"@id": u"public"}, #TODO
            u"published": "2014-06-03T15:28:31.000000Z",
            u"modified": "2014-06-03T15:28:31.000000Z"
        }
        self.assertEquals(object.to_dict(), openDataAsDict)
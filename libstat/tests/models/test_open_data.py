from datetime import datetime
from bibstat import settings
from libstat.models import Variable
from libstat.models import OpenData
from libstat.tests import MongoTestCase


class OpenDataTest(MongoTestCase):

    def setUp(self):
        v = Variable(key="folk5", description="Antal bemannade serviceställen, sammanräknat", type="integer",
                     is_public=True, target_groups=["folkbib"])
        v.save()
        publishing_date = datetime(2014, 6, 3, 15, 28, 31)
        d1 = OpenData(library_name="KARLSTAD STADSBIBLIOTEK", sigel="323", sample_year=2013,
                      target_group="folkbib", variable=v, value=6, date_created=publishing_date,
                      date_modified=publishing_date)
        d1.save()
        d2 = OpenData(library_name="NORRBOTTENS LÄNSBIBLIOTEK", sample_year=2013, target_group="folkbib", variable=v,
                      value=6, date_created=publishing_date, date_modified=publishing_date)
        d2.save()

    def test_should_transform_object_with_sigel_to_dict(self):
        object = OpenData.objects.get(library_name="KARLSTAD STADSBIBLIOTEK")
        openDataAsDict = {
            "@id": str(object.id),
            "@type": "Observation",
            "folk5": 6,
            "library": {
                "@id": "{}/library/323".format(settings.BIBDB_BASE_URL),
                "name": "KARLSTAD STADSBIBLIOTEK"
            },
            "sampleYear": 2013,
            "targetGroup": "Folkbibliotek",
            # u"targetGroup": {u"@id": u"public"}, #TODO
            "published": "2014-06-03T15:28:31.000000Z",
            "modified": "2014-06-03T15:28:31.000000Z"
        }
        self.assertEqual(object.to_dict(), openDataAsDict)

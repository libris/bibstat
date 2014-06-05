# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.conf import settings

import json
import datetime

from libstat.models import Variable, OpenData

"""
    OpenDataApi
    TODO: DO this for now?
    "library": { "name": "BOTKYRKA BIBILIOTEK" },
        
"""
def data_api(request):
    date_format = "%Y-%m-%d"
    
    from_date = request.GET.get("from_date", datetime.date.fromtimestamp(0))
    to_date = request.GET.get("to_date", datetime.date.today() + datetime.timedelta(days=1))
    limit = int(request.GET.get("limit", 100))
    offset = int(request.GET.get("offset", 0))
    
    print u"Fetching statistics data published between {} and {}, items {} to {}".format(from_date, to_date, offset, offset + limit)
    
    objects = OpenData.objects.filter(date_modified__gte=from_date, date_modified__lt=to_date).skip(offset).limit(limit)
    observations = []
    for item in objects:
        observations.append(item.to_dict())
    data = {
        u"@context": {
            u"observations": u"@graph",
            u"@vocab": u"{}/def/terms#".format(settings.API_BASE_URL)
        },
        u"observations": observations
    }
        
    return HttpResponse(json.dumps(data), content_type="application/json")


"""
    TermsApi
"""
def terms_api(request):
    vars = {}
    vars[u"library"] = {
        u"@id": u"{}/data/library".format(settings.API_BASE_URL),
        u"@type": u"@id",
        u"label": u"Bibliotek"
    }
    vars[u"sampleYear"] = {
        u"@id": u"{}/def/terms#sampleYear".format(settings.API_BASE_URL),
        u"@type": u"xsd:gYear",
        u"label": u"Det mätår som statistikuppgiften avser"
    }
    vars[u"targetGroup"] = {
        u"@id": u"{}/def/terms#targetGroup".format(settings.API_BASE_URL),
        u"@type": u"xsd:string",
        u"label": u"Den målgrupp som svarande bibliotek ingår i."
    }
    vars[u"modified"] = {
        u"@id": u"{}/def/terms#modified".format(settings.API_BASE_URL),
        u"@type": u"xsd:DateTime",
        u"label": u"Datum då mätvärdet senast uppdaterades"
    }
    vars[u"published"] = {
        u"@id": u"{}/def/terms#published".format(settings.API_BASE_URL),
        u"@type": u"xsd:dateTime",
        u"label": u"Datum då mätvärdet först publicerades"
    }
    variables = Variable.objects.filter(is_public=True).order_by("key")
    for v in variables:
        vars[v.key] = v.to_dict()
    
    terms = {
        u"@context": {
            u"xsd": u"http://www.w3.org/2001/XMLSchema#",
            u"@language": u"sv",
            u"index": {
                u"@container": u"@index",
                u"@id": u"@graph"
            }              
        },
        u"index": vars
    }
    return HttpResponse(json.dumps(terms), content_type="application/json")


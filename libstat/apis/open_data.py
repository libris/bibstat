# -*- coding: utf-8 -*-
import datetime
import json
import logging

from django.http import HttpResponse, Http404
from mongoengine import Q

from bibstat import settings
from libstat.models import Variable, OpenData
from libstat.utils import parse_datetime_from_isodate_str

logger = logging.getLogger(__name__)


data_context = {
    u"@vocab": u"{}/def/terms/".format(settings.API_BASE_URL),
    u"xsd": u"http://www.w3.org/2001/XMLSchema#",
    u"qb": u"http://purl.org/linked-data/cube#",
    u"xhv": u"http://www.w3.org/1999/xhtml/vocab#",
    u"foaf": u"http://xmlns.com/foaf/0.1/",
    u"@base": u"{}/data/".format(settings.API_BASE_URL),
    u"@language": u"sv",
    u"DataSet": u"qb:DataSet",
    u"Observation": u"qb:Observation",
    u"observations": {u"@id": u"qb:observation", u"@container": u"@set"},
    u"dataSet": {u"@id": u"qb:dataSet", u"@type": u"@id"},
    u"next": {u"@id": u"xhv:next", u"@type": u"@id"},
    u"published": {u"@type": "xsd:dateTime"},
    u"modified": {u"@type": "xsd:dateTime"},
    u"name": u"foaf:name"
}

data_set = {
    "@context": data_context,
    "@id": "",
    "@type": "DataSet",
    u"label": u"Sveriges biblioteksstatistik"
}

def data_api(request):
    from_date = parse_datetime_from_isodate_str(request.GET.get("from_date", None))
    to_date = parse_datetime_from_isodate_str(request.GET.get("to_date", None))
    limit = int(request.GET.get("limit", 100))
    offset = int(request.GET.get("offset", 0))
    term = request.GET.get("term", None)

    if not from_date:
        from_date = datetime.datetime.fromtimestamp(0)
    if not to_date:
        to_date = datetime.datetime.today() + datetime.timedelta(days=1)

    modified_from_query = Q(date_modified__gte=from_date)
    modified_to_query = Q(date_modified__lt=to_date)

    objects = []
    if term:
        try:
            variable = Variable.objects.get(key=term)
            logger.debug(
                u"Fetching statistics data for term {} published between {} and {}, items {} to {}".format(
                    variable.key,
                    from_date,
                    to_date,
                    offset,
                    offset + limit))
            objects = OpenData.objects.filter(Q(variable=variable) & modified_from_query & modified_to_query).skip(
                offset).limit(limit)
        except Exception:
            logger.warn(u"Unknown variable {}, skipping..".format(term))

    else:
        logger.debug(
            u"Fetching statistics data published between {} and {}, items {} to {}".format(
                from_date, to_date, offset, offset + limit))
        objects = OpenData.objects.filter(modified_from_query & modified_to_query).skip(offset).limit(limit)

    observations = []
    for item in objects:
        if item.is_active:
            observations.append(item.to_dict())

    data = dict(data_set, observations=observations)
    if len(observations) >= limit:
        data[u"next"] = u"?limit={}&offset={}".format(limit, offset + limit)

    return HttpResponse(json.dumps(data), content_type="application/ld+json")


def observation_api(request, observation_id):
    try:
        open_data = OpenData.objects.get(pk=observation_id)
    except Exception:
        raise Http404
    observation = {u"@context": data_context}
    observation.update(open_data.to_dict())
    observation["dataSet"] = data_set["@id"]
    return HttpResponse(json.dumps(observation), content_type="application/ld+json")

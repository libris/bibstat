import datetime
import json
import logging
from time import strftime

from django.http import (
    HttpResponse,
    Http404,
    HttpResponseBadRequest,
    HttpResponseNotFound,
)
from wsgiref.util import FileWrapper
from mongoengine import Q

from bibstat import settings
from libstat.models import Variable, OpenData
from libstat.services.excel_export import public_excel_workbook
from libstat.utils import parse_datetime_from_isodate_str

logger = logging.getLogger(__name__)


data_context = {
    "@vocab": "{}/def/terms/".format(settings.API_BASE_URL),
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "qb": "http://purl.org/linked-data/cube#",
    "xhv": "http://www.w3.org/1999/xhtml/vocab#",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "@base": "{}/data/".format(settings.API_BASE_URL),
    "@language": "sv",
    "DataSet": "qb:DataSet",
    "Observation": "qb:Observation",
    "observations": {"@id": "qb:observation", "@container": "@set"},
    "dataSet": {"@id": "qb:dataSet", "@type": "@id"},
    "next": {"@id": "xhv:next", "@type": "@id"},
    "published": {"@type": "xsd:dateTime"},
    "modified": {"@type": "xsd:dateTime"},
    "name": "foaf:name",
}

data_set = {
    "@context": data_context,
    "@id": "",
    "@type": "DataSet",
    "label": "Sveriges biblioteksstatistik",
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
    is_active_query = Q(is_active=True)

    objects = []
    if term:
        try:
            variable = Variable.objects.get(key=term)
            logger.debug(
                "Fetching statistics data for term {} published between {} and {}, items {} to {}".format(
                    variable.key, from_date, to_date, offset, offset + limit
                )
            )
            objects = (
                OpenData.objects.filter(
                    Q(variable=variable)
                    & modified_from_query
                    & modified_to_query
                    & is_active_query
                )
                .skip(offset)
                .limit(limit)
            )
        except Exception:
            logger.warn("Unknown variable {}, skipping..".format(term))

    else:
        logger.debug(
            "Fetching statistics data published between {} and {}, items {} to {}".format(
                from_date, to_date, offset, offset + limit
            )
        )
        objects = (
            OpenData.objects.filter(
                modified_from_query & modified_to_query & is_active_query
            )
            .skip(offset)
            .limit(limit)
        )

    observations = []
    for item in objects:
        observations.append(item.to_dict())

    data = dict(data_set, observations=observations)
    if len(observations) >= limit:
        data["next"] = "?limit={}&offset={}".format(limit, offset + limit)

    return HttpResponse(json.dumps(data), content_type="application/ld+json")


def observation_api(request, observation_id):
    try:
        open_data = OpenData.objects.get(pk=observation_id)
    except Exception:
        raise Http404
    observation = {"@context": data_context}
    observation.update(open_data.to_dict())
    observation["dataSet"] = data_set["@id"]
    return HttpResponse(json.dumps(observation), content_type="application/ld+json")


def export_api(request):
    if request.method == "GET":

        sample_year = request.GET.get("sample_year", None)
        if not sample_year:
            return HttpResponseBadRequest()

        try:
            sample_year = int(sample_year)
        except ValueError:
            return HttpResponseBadRequest()

        valid_sample_years = set(OpenData.objects.distinct("sample_year"))
        if sample_year not in valid_sample_years:
            return HttpResponseNotFound()

        filename = "Biblioteksstatistik för {} ({}).xlsx".format(
            sample_year, strftime("%Y-%m-%d %H.%M.%S")
        )
        path = public_excel_workbook(sample_year)

        response = HttpResponse(
            FileWrapper(open(path, "rb")), content_type="application/vnd.ms-excel"
        )
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)
        return response

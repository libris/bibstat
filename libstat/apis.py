# -*- coding: utf-8 -*-
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core.urlresolvers import reverse

from mongoengine.queryset import Q

import json
import datetime

from libstat.models import Variable, OpenData
from libstat.utils import parse_datetime_from_isodate_str

data_context = {
    u"@vocab": u"{}/def/terms/".format(settings.API_BASE_URL),
    u"@base": u"{}/data/".format(settings.API_BASE_URL),
    u"@language": u"sv",
    u"foaf": u"http://xmlns.com/foaf/0.1/",
    u"name": u"foaf:name",
    u"observations": u"@graph"
}

term_context = {
    u"xsd": u"http://www.w3.org/2001/XMLSchema#",
    u"rdf": u"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    u"rdfs": u"http://www.w3.org/2000/01/rdf-schema#",
    u"owl": u"http://www.w3.org/2002/07/owl#",
    u"qb": u"http://purl.org/linked-data/cube#",
    u"@language": u"sv",
    u"label": u"rdfs:label",
    u"range": {u"@id": u"rdfs:range", u"@type": u"@id"},
    u"comment": u"rdfs:comment",
    u"subClassOf": {u"@id": u"rdfs:subClassOf", u"@type": u"@id"},
    u"@base": u"{}/def/terms/".format(settings.API_BASE_URL),
    u"terms": {u"@reverse": u"rdfs:isDefinedBy"}
}

terms_vocab = {
    "@context": term_context,
    "@id": "",
    "@type": "owl:Ontology",
    u"label": u"Termer för Sveriges biblioteksstatistik"
}

core_terms = [
    {
        u"@id": u"library",
        u"@type": [u"rdf:Property", u"qb:DimensionProperty"],
        u"range": u"https://schema.org/Organization",
        u"label": u"Bibliotek"
    },
    {
        u"@id": u"sampleYear",
        u"@type": [u"rdf:Property", u"qb:DimensionProperty"],
        u"label": u"Mätår",
        u"comment": u"Det mätår som statistikuppgiften avser",
        u"range": u"xsd:gYear"
    },
    {
        u"@id": u"targetGroup",
        u"@type": [u"rdf:Property", u"qb:DimensionProperty"],
        u"label": u"Målgrupp",
        u"comment": u"Den målgrupp som svarande bibliotek ingår i.",
        u"range": u"xsd:string"
    },
    {
        u"@id": u"modified",
        u"@type": u"rdf:Property",
        u"label": u"Uppdaterad",
        u"comment": u"Datum då mätvärdet senast uppdaterades",
        u"range": u"xsd:dateTime"
    },
    {
        u"@id": u"published",
        u"@type": u"rdf:Property",
        u"label": u"Publicerad",
        u"comment": u"Datum då mätvärdet först publicerades",
        u"range": u"xsd:dateTime"
    },
    {
        u"@id": u"Observation",
        u"@type": u"rdfs:Class", 
        u"label": u"Observation",
        u"comment": u"En observation för ett bibiliotek, mätår och variabel",
        u"subClassOf": u"qb:Observation"
    }
]

core_term_ids = {term [u"@id"] for term in core_terms}

"""
    OpenDataApi
"""
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
            print u"Fetching statistics data for term {} published between {} and {}, items {} to {}".format(variable.key, from_date, to_date, offset, offset + limit)
            objects = OpenData.objects.filter(Q(variable=variable) & modified_from_query & modified_to_query).skip(offset).limit(limit)
        except Exception:
            print u"Unknown variable {}, skipping..".format(term)
            
    else:
        print u"Fetching statistics data published between {} and {}, items {} to {}".format(from_date, to_date, offset, offset + limit)
        objects = OpenData.objects.filter(modified_from_query & modified_to_query).skip(offset).limit(limit)

    observations = []
    for item in objects:
        observations.append(item.to_dict())
    
    data = {u"@context": data_context, u"observations": observations}
    
    return HttpResponse(json.dumps(data), content_type="application/ld+json")


"""
    Observation Api
"""
def observation_api(request, observation_id):
    try:
        open_data = OpenData.objects.get(pk=observation_id)
    except Exception:
        raise Http404
    observation = {u"@context": data_context}
    observation.update(open_data.to_dict())
    return HttpResponse(json.dumps(observation), content_type="application/ld+json")

"""
    TermsApi
"""
def terms_api(request):
    terms = core_terms[:]
    variables = Variable.objects.filter(is_public=True).order_by("key")
    for v in variables:
        terms.append(v.to_dict())
    data = dict(terms_vocab, terms=terms)
    return HttpResponse(json.dumps(data), content_type="application/ld+json")

def term_api(request, term_key):
    try:
        term = Variable.objects.get(key=term_key)
    except Exception:
        if term_key in core_term_ids:
            http303 = HttpResponse(content="", status=303)
            http303["Location"] = reverse("terms_api")
            return http303
        else:
            raise Http404
    data = {u"@context": term_context}
    data.update(term.to_dict())
    data["rdfs:isDefinedBy"] = {"@id": terms_vocab["@id"]}
    return HttpResponse(json.dumps(data), content_type="application/ld+json")

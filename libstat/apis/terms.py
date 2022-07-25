import json
from django.urls import reverse
from django.http import HttpResponse, Http404
from bibstat import settings
from libstat.models import Variable


term_context = {
    u"xsd": u"http://www.w3.org/2001/XMLSchema#",
    u"rdf": u"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    u"rdfs": u"http://www.w3.org/2000/01/rdf-schema#",
    u"owl": u"http://www.w3.org/2002/07/owl#",
    u"dcterms": "http://purl.org/dc/terms/",
    u"qb": u"http://purl.org/linked-data/cube#",
    u"@base": u"{}/def/terms/".format(settings.API_BASE_URL),
    u"@language": u"sv",
    u"label": u"rdfs:label",
    u"range": {u"@id": u"rdfs:range", u"@type": u"@id"},
    u"comment": u"rdfs:comment",
    u"subClassOf": {u"@id": u"rdfs:subClassOf", u"@type": u"@id"},
    u"subPropertyOf": {u"@id": u"rdfs:subPropertyOf", u"@type": u"@id"},
    u"isDefinedBy": {u"@id": u"rdfs:isDefinedBy", u"@type": u"@id"},
    u"terms": {u"@reverse": u"rdfs:isDefinedBy"},
    u"replaces": {u"@id": u"dcterms:replaces", u"@type": u"@id"},
    u"replacedBy": {u"@id": u"dcterms:isReplacedBy", u"@type": u"@id"},
    u"valid": {u"@id": u"dcterms:valid", u"@type": u"dcterms:Period"},
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
        u"subPropertyOf": "dcterms:modified",
        u"label": u"Uppdaterad",
        u"comment": u"Datum då mätvärdet senast uppdaterades",
        u"range": u"xsd:dateTime"
    },
    {
        u"@id": u"published",
        u"@type": u"rdf:Property",
        u"subPropertyOf": "dcterms:issued",
        u"label": u"Publicerad",
        u"comment": u"Datum då mätvärdet först publicerades",
        u"range": u"xsd:dateTime"
    },
    {
        u"@id": u"Observation",
        u"@type": u"rdfs:Class",
        u"subClassOf": u"qb:Observation",
        u"label": u"Observation",
        u"comment": u"En observation för ett bibiliotek, mätår och variabel"
    }
]

core_term_ids = {term[u"@id"] for term in core_terms}


def term_api(request, term_key):
    try:
        term = Variable.objects.public_term_by_key(term_key)
    except Exception:
        if term_key in core_term_ids:
            http303 = HttpResponse(content="", status=303)
            http303["Location"] = reverse("terms_api")
            return http303
        else:
            raise Http404
    data = {u"@context": term_context}
    data.update(term.to_dict())
    data["isDefinedBy"] = terms_vocab["@id"]
    return HttpResponse(json.dumps(data), content_type="application/ld+json")


def terms_api(request):
    terms = core_terms[:]

    variables = Variable.objects.public_terms()
    for v in variables:
        terms.append(v.to_dict())
    data = dict(terms_vocab, terms=terms)
    return HttpResponse(json.dumps(data), content_type="application/ld+json")
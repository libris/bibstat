import json
from django.urls import reverse
from django.http import HttpResponse, Http404
from bibstat import settings
from libstat.models import Variable


term_context = {
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "dcterms": "http://purl.org/dc/terms/",
    "qb": "http://purl.org/linked-data/cube#",
    "@base": "{}/def/terms/".format(settings.API_BASE_URL),
    "@language": "sv",
    "label": "rdfs:label",
    "range": {"@id": "rdfs:range", "@type": "@id"},
    "comment": "rdfs:comment",
    "subClassOf": {"@id": "rdfs:subClassOf", "@type": "@id"},
    "subPropertyOf": {"@id": "rdfs:subPropertyOf", "@type": "@id"},
    "isDefinedBy": {"@id": "rdfs:isDefinedBy", "@type": "@id"},
    "terms": {"@reverse": "rdfs:isDefinedBy"},
    "replaces": {"@id": "dcterms:replaces", "@type": "@id"},
    "replacedBy": {"@id": "dcterms:isReplacedBy", "@type": "@id"},
    "valid": {"@id": "dcterms:valid", "@type": "dcterms:Period"},
}

terms_vocab = {
    "@context": term_context,
    "@id": "",
    "@type": "owl:Ontology",
    "label": "Termer för Sveriges biblioteksstatistik"
}

core_terms = [
    {
        "@id": "library",
        "@type": ["rdf:Property", "qb:DimensionProperty"],
        "range": "https://schema.org/Organization",
        "label": "Bibliotek"
    },
    {
        "@id": "sampleYear",
        "@type": ["rdf:Property", "qb:DimensionProperty"],
        "label": "Mätår",
        "comment": "Det mätår som statistikuppgiften avser",
        "range": "xsd:gYear"
    },
    {
        "@id": "targetGroup",
        "@type": ["rdf:Property", "qb:DimensionProperty"],
        "label": "Målgrupp",
        "comment": "Den målgrupp som svarande bibliotek ingår i.",
        "range": "xsd:string"
    },
    {
        "@id": "modified",
        "@type": "rdf:Property",
        "subPropertyOf": "dcterms:modified",
        "label": "Uppdaterad",
        "comment": "Datum då mätvärdet senast uppdaterades",
        "range": "xsd:dateTime"
    },
    {
        "@id": "published",
        "@type": "rdf:Property",
        "subPropertyOf": "dcterms:issued",
        "label": "Publicerad",
        "comment": "Datum då mätvärdet först publicerades",
        "range": "xsd:dateTime"
    },
    {
        "@id": "Observation",
        "@type": "rdfs:Class",
        "subClassOf": "qb:Observation",
        "label": "Observation",
        "comment": "En observation för ett bibiliotek, mätår och variabel"
    }
]

core_term_ids = {term["@id"] for term in core_terms}


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
    data = {"@context": term_context}
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
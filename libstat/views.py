# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404

from libstat.models import Variable, SurveyResponse, OpenData
from django.contrib.auth.decorators import permission_required
import json
from django.conf import settings

# Create your views here.

def index(request):
    context =  {
        "nav_start_css": "active",
        "nav_open_data_css": ""
    }
    return render(request, 'libstat/index.html', context)
  
def open_data(request):
    context =  {
        "nav_start_css": "",
        "nav_open_data_css": "active"
    }
    return render(request, 'libstat/open_data.html', context)

"""

    TODO: DO this for now?
    "library": { "name": "BOTKYRKA BIBILIOTEK" },
    
LAB:
{

    "@context": {
        "observations": "@graph",
          "xsd": "http://www.w3.org/2001/XMLSchema#",
        "@language": "sv",
          "library": {
                "@id": "http://localhost:8000/statistics/data/library",
                "@type": "@id",
                "label": "Bibliotek"

        },
        "sampleYear": {
            "@id": "http://localhost:8000/statistics/def/terms#sampleYear",
            "@type": "xsd:gYear",
            "label": "Det mätår som statistiken avser."

        },
          "targetGroup": {
          "@id": "http://localhost:8000/statistics/def/terms#targetGroup",
          "@type": "xsd:string",
          "label": "Den målgrupp som svarande bibliotek ingår i."
          },
          "modified": {
          "@id": "http://localhost:8000/statistics/def/terms#modified",
          "@type": "http://schema.org/DateTime",
          "label": "Datum då mätvärdet senast uppdaterades"
          },
          "published": {
            "@id": "http://localhost:8000/statistics/def/terms#published",
                "@type": "http://schema.org/DateTime",
                "label": "Datum då mätvärdet först publicerades"
          },
          "forsk56": {
            "@id": "http://localhost:8000/statistics/def/terms#forsk56",
            "@type": "xsd:integer",
            "label": "Nyförvärv Mikrografiska dokument - antal fysiska enheter"
        },
        "forsk55": {
            "@id": "http://localhost:8000/statistics/def/terms#forsk55",
            "@type": "xsd:integer",
            "label": "Bestånd Mikrografiska dokument - antal fysiska enheter"
        }
    },
    "observations": [
        {
            "forsk55": 880,
            "modified": "2014-06-03T08:46:46Z",
            "library": "VTI Statens väg- och transportforskningsinstitut. BIC",
            "sampleYear": 2011,
            "published": "2014-06-03T08:46:46Z",
            "targetGroup": "research"
        },
        {
          "forsk56": null,
            "modified": "2014-06-03T08:46:46Z",
            "library": "VTI Statens väg- och transportforskningsinstitut. BIC",
            "sampleYear": 2011,
            "published": "2014-06-03T08:46:46Z",
            "targetGroup": "research"
        }
    ]

}
    
"""
def data(request):
    date_format = "%Y-%m-%d"
    
    from_date = request.GET.get("from_date", None)
    to_date = request.GET.get("to_date", None)
    limit = int(request.GET.get("limit", 100))
    offset = int(request.GET.get("offset", 0))
    
    print u"Fetching statistics data published between {} and {}, items {} to {}".format(from_date, to_date, offset, offset+limit)
    
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

def terms(request):
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
  
@permission_required('is_superuser', login_url='login')
def variables(request):
    target_group = request.GET.get("target_group", "")
    if target_group:
      variables = Variable.objects.filter(target_groups__in=[target_group])
    else:
      variables = Variable.objects.order_by("key")
    context = { 
        'variables': variables,
        'target_group': target_group
    }
    return render(request, 'libstat/variables.html', context)

@permission_required('is_superuser', login_url='login')
def variable_detail(request, variable_id):
    try: 
        v = Variable.objects.get(pk=variable_id)
    except Exception:
        raise Http404
    context = {'variable': v }
    return render(request, 'libstat/variable_detail.html', context)

@permission_required('is_superuser', login_url='login')
def survey_responses(request):
    s_responses = []
    
    # TODO: Cache sample_years
    sample_years = SurveyResponse.objects.distinct("sample_year")
    
    if request.method == "POST":
      target_group = request.POST.get("target_group", "")
      sample_year = request.POST.get("sample_year", "")
      
      print(u"Publish requested for {} {}".format(target_group, sample_year))
      
      s_responses = SurveyResponse.objects.by_year_or_group(sample_year=sample_year, target_group=target_group)
      for sr in s_responses:
        sr.publish()
      
      # TODO: There has to be a better way to do this...
      return HttpResponseRedirect(u"{}{}".format(reverse("survey_responses"), u"?action=list&target_group={}&sample_year={}".format(target_group, sample_year)))
        
    action = request.GET.get("action", "")
    target_group = request.GET.get("target_group", "")
    sample_year = request.GET.get("sample_year", "")
    
    if action == "list":
      s_responses = SurveyResponse.objects.by_year_or_group(sample_year=sample_year, target_group=target_group).order_by("library")
  
    context = { 
         'sample_years': sample_years,
         'survey_responses': s_responses, 
         'target_group': target_group,
         'sample_year': sample_year
    }
    return render(request, 'libstat/survey_responses.html', context)

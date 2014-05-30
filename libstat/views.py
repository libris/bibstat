# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404

from libstat.models import Variable, SurveyResponse
from django.contrib.auth.decorators import permission_required

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
      action = request.POST.get("action", "list")
      target_group = request.POST.get("target_group", "")
      sample_year = request.POST.get("sample_year", "")
    
      if target_group and sample_year:
        if action == "publish":
          print u"Publish called for {} {}".format(target_group, sample_year)
        else:
          s_responses = SurveyResponse.objects.filter(target_group=target_group, sample_year=sample_year).order_by("library")
    
    context = { 
         'sample_years': sample_years,
         'survey_responses': s_responses 
    }
    return render(request, 'libstat/survey_responses.html', context)

"""
Slice/DataSet
{
    "slice": "slice_noOfEmployees_byYear",
    "observations": [
        {

            "refArea": "Karlstad",
            "sampleYear": 2013
            "staffType": "Librarian",
            "sex": "Male"
            "noOfEmployees": 6
        },
        {
            "refArea": "Karlstad",
            "sampleYear": 2013
            "staffType": "Librarian",
            "sex": "Female"
            "noOfEmployees": 23
        },
        {

            "refArea": "Enköping",
            "sampleYear": 2013
            "staffType": "Librarian",
            "sex": "Male"
            "noOfEmployees": 8
        },
        {
            "refArea": "Enköping",
            "sampleYear": 2013
            "staffType": "Librarian",
            "sex": "Female"
            "sex": "Female"
            "noOfEmployees": 13
        }
    ]
}
"""

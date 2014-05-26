# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404

from libstat.models import Variable, SurveyResponse


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

def variables(request):
    variables = Variable.objects.all()
    context = { 'variables': variables }
    return render(request, 'libstat/variables.html', context)

def variable_detail(request, variable_id):
    try: 
        v = Variable.objects.get(pk=variable_id)
    except Exception:
        raise Http404
    context = {'variable': v }
    return render(request, 'libstat/variable_detail.html', context)

def survey_responses(request):
    s_responses = SurveyResponse.objects.all()
    context = { 'survey_responses': s_responses }
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
            "noOfEmployees": 13
        }
    ]
}
"""

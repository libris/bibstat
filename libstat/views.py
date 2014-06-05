# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404

from libstat.models import Variable, SurveyResponse
from django.contrib.auth.decorators import permission_required

from libstat.apis import *

def index(request):
    context = {
        "nav_start_css": "active",
        "nav_open_data_css": ""
    }
    return render(request, 'libstat/index.html', context)

def open_data(request):
    context = {
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

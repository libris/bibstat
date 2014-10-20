# -*- coding: utf-8 -*-
import json
import logging

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from mongoengine import Q

from libstat.models import Variable


logger = logging.getLogger(__name__)


@permission_required('is_superuser', login_url='index')
def surveyable_variables_api(request):
    """
        Helper Json API method to populate search field for surveyable variable when constructing a Survey. (Ajax call)
    """
    query = request.REQUEST.get("q", None)
    if query:
        variables = Variable.objects.surveyable().filter(key__icontains=query)
    else:
        variables = Variable.objects.surveyable()
    data = [{'key': v.key, 'id': str(v.id)} for v in variables]
    return HttpResponse(json.dumps(data), content_type="application/json")


@permission_required('is_superuser', login_url='index')
def replaceable_variables_api(request):
    """
        Helper Json API method to populate search field for replaceable variables. (Ajax call)
    """
    query = request.REQUEST.get("q", None)
    if query:
        key_query = Q(key__icontains=query)
        description_query = Q(description__icontains=query)
        variables = Variable.objects.replaceable().filter(key_query | description_query)
    else:
        variables = Variable.objects.replaceable()
    data = [v.as_simple_dict() for v in variables]
    return HttpResponse(json.dumps(data), content_type="application/json")

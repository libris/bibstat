# -*- coding: utf-8 -*-
import json
import logging

from django.core.urlresolvers import reverse

from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse, Http404
from django.contrib.auth.decorators import permission_required
from mongoengine.errors import NotUniqueError

from libstat.models import Variable
from libstat.forms.variable import VariableForm
from libstat.utils import SURVEY_TARGET_GROUPS


logger = logging.getLogger(__name__)


@permission_required('is_superuser', login_url='index')
def variables(request):
    target_groups = request.GET.getlist("target_group", [])
    if target_groups:
        if target_groups == [u"all"]:
            #target_group_filter = [g[0] for g in SURVEY_TARGET_GROUPS]
            target_group_filter = (u"sjukbib", u"skolbib", u"specbib", u"folkbib")
            variables = Variable.objects.filter(target_groups__all=target_group_filter)
        else:
            target_group_filter = target_groups
            variables = Variable.objects.filter(target_groups__in=target_group_filter)
    else:
        variables = Variable.objects.all()
    context = {
        'variables': variables,
        'target_groups': target_groups,
        'nav_variables_css': 'active'
    }
    return render(request, 'libstat/variables.html', context)


@permission_required('is_superuser', login_url='login')
def create_variable(request):
    """
        Modal view.
        Create a new draft Variable instance.
    """
    context = {
        'mode': 'create',
        'form_url': reverse("create_variable"),
        'modal_title': u"Ny term (utkast)"
    }
    if request.method == "POST":
        errors = {}
        form = VariableForm(request.POST)
        if form.is_valid():
            try:
                v = form.save(user=request.user)
                # No redirect since this is displayed as a modal and we do a javascript redirect if no form errors
                return HttpResponse(v.to_json(), content_type="application/json")
            except NotUniqueError as nue:
                logger.warning(u"A Variable with key {} already exists: {}".format(form.fields["key"], nue))
                errors['key'] = [u"Det finns redan en term med nyckel {}".format(form.fields["key"])]
            except Exception as e:
                logger.warning(u"Error creating Variable: {}".format(e))
                errors['__all__'] = [u"Kan inte skapa term {}".format(form.fields["key"])]
        else:
            errors = form.errors
            context['errors'] = errors
            return HttpResponse(json.dumps(context), content_type="application/json")

    else:
        form = VariableForm()

    context['form'] = form
    return render(request, 'libstat/variable/edit.html', context)


@permission_required('is_superuser', login_url='login')
def edit_variable(request, variable_id):
    """
        Edit variable modal view
    """

    try:
        v = Variable.objects.get(pk=variable_id)
    except Exception:
        raise Http404

    context = {
        'mode': 'edit',
        'form_url': reverse("edit_variable", kwargs={"variable_id": variable_id}),
        'modal_title': u"{} ({})".format(v.key, v.state["label"]) if not v.state["state"] == u"current" else v.key
    }

    if request.method == "POST":
        action = request.POST.get("submit_action", "save")

        errors = {}
        form = VariableForm(request.POST, instance=v)
        if form.is_valid():
            try:
                if action == "delete":
                    if v.is_deletable():
                        v.delete()
                    else:
                        return HttpResponseForbidden()
                else:
                    v = form.save(user=request.user, activate=(action == "save_and_activate"))

                # No redirect since this is displayed as a modal and we do a javascript redirect if no form errors
                return HttpResponse(v.to_json(), content_type="application/json")

            except NotUniqueError as nue:
                logger.warning(u"A Variable with key {} already exists: {}".format(v.key, nue))
                errors['key'] = [u"Det finns redan en term med nyckel {}".format(v.key)]
            except Exception as e:
                logger.warning(u"Error updating Variable {}: {}".format(variable_id, e))
                errors['__all__'] = [u"Kan inte uppdatera term {}".format(v.key)]

        else:
            errors = form.errors
        context['errors'] = errors
        return HttpResponse(json.dumps(context), content_type="application/json")
    else:
        form = VariableForm(instance=v)

    context['form'] = form
    return render(request, 'libstat/variable/edit.html', context)

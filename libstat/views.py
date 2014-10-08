# -*- coding: utf-8 -*-
from time import strftime

from django.shortcuts import render, redirect, resolve_url
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.utils.http import is_safe_url
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from mongoengine.errors import NotUniqueError
from django.forms.util import ErrorList
from excel_response import ExcelResponse

from libstat.models import Section, Group, Cell, SurveyObs, Row
from libstat.forms import *
from libstat.apis import *


logger = logging.getLogger(__name__)


def index(request):
    context = {
        "nav_start_css": "active",
        "nav_open_data_css": ""
    }
    return render(request, 'libstat/index.html', context)


def open_data(request):
    context = {
        "nav_start_css": "",
        "nav_open_data_css": "active",
        "api_base_url": settings.API_BASE_URL
    }
    return render(request, 'libstat/open_data.html', context)


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request):
    """
        Login modal view
    """
    redirect_to = _get_listview_from_modalview(request.REQUEST.get("next", ""))

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            context = {
                'next': redirect_to
            }
            return HttpResponse(json.dumps(context), content_type="application/json")
        else:
            context = {
                'errors': form.errors,
                'next': redirect_to
            }
            return HttpResponse(json.dumps(context), content_type="application/json")

    else:
        form = AuthenticationForm(request)

    context = {
        'form': form,
        'next': redirect_to,
    }
    return render(request, 'libstat/modals/login.html', context)


def _get_listview_from_modalview(relative_url=""):
    if reverse("variables") in relative_url:
        return reverse("variables")
    return relative_url


@permission_required('is_superuser', login_url='index')
def variables(request):
    target_groups = request.GET.getlist("target_group", [])
    if target_groups:
        if target_groups == [u"all"]:
            target_group_filter = [g[0] for g in SURVEY_TARGET_GROUPS]
            variables = Variable.objects.filter(target_groups__all=target_group_filter)
        else:
            target_group_filter = target_groups
            variables = Variable.objects.filter(target_groups__in=target_group_filter)
    else:
        variables = Variable.objects.all()
    context = {
        'variables': variables,
        'target_group': target_groups
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
    return render(request, 'libstat/modals/edit_variable.html', context)


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
                    v = form.save(user=request.user, activate=(action == "save_and_activate"));

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
    return render(request, 'libstat/modals/edit_variable.html', context)


@permission_required('is_superuser', login_url='index')
def survey_responses(request):
    s_responses = []
    message = ""

    # TODO: Cache sample_years
    sample_years = SurveyResponse.objects.distinct("sample_year")
    sample_years.sort()
    sample_years.reverse()

    action = request.GET.get("action", "")
    target_group = request.GET.get("target_group", "")
    sample_year = request.GET.get("sample_year", "")
    unpublished_only = request.GET.get("unpublished_only", False);
    if "True" == unpublished_only:
        unpublished_only = True
    else:
        unpublished_only = False

    if action == "list":
        # TODO: Pagination
        if unpublished_only:
            s_responses = SurveyResponse.objects.unpublished_by_year_or_group(sample_year=sample_year,
                                                                              target_group=target_group).order_by(
                "library")
        elif sample_year or target_group:
            s_responses = SurveyResponse.objects.by_year_or_group(sample_year=sample_year,
                                                                  target_group=target_group).order_by("library")
        else:
            message = u"Ange åtminstone ett urvalskriterium för att lista enkätsvar"

    context = {
        'sample_years': sample_years,
        'survey_responses': s_responses,
        'target_group': target_group,
        'sample_year': sample_year,
        'unpublished_only': unpublished_only,
        'bibdb_library_base_url': u"{}/library".format(settings.BIBDB_BASE_URL),
        'message': message
    }
    return render(request, 'libstat/survey_responses.html', context)


@permission_required('is_superuser', login_url='index')
def publish_survey_responses(request):
    MAX_PUBLISH_LIMIT = 500

    if request.method == "POST":
        target_group = request.POST.get("target_group", "")
        sample_year = request.POST.get("sample_year", "")
        survey_response_ids = request.POST.getlist("survey-response-ids", [])

        logger.info(u"Publish requested for {} survey response ids".format(len(survey_response_ids)))

        if len(survey_response_ids) > MAX_PUBLISH_LIMIT:
            survey_response_ids = survey_response_ids[:MAX_PUBLISH_LIMIT]
            logger.warning(
                u"That seems like an awful lot of objects to handle in one transaction, limiting to first {}".format(
                    MAX_PUBLISH_LIMIT))

        if len(survey_response_ids) > 0:
            s_responses = SurveyResponse.objects.filter(id__in=survey_response_ids)
            for sr in s_responses:
                try:
                    sr.publish(user=request.user)
                except Exception as e:
                    logger.error(u"Error when publishing survey response {}:".format(sr.id))
                    print e

    # TODO: There has to be a better way to do this...
    return HttpResponseRedirect(u"{}{}".format(reverse("survey_responses"),
                                               u"?action=list&target_group={}&sample_year={}".format(target_group,
                                                                                                     sample_year)))


@permission_required('is_superuser', login_url='index')
def export_survey_responses(request):
    if request.method == "POST":
        survey_response_ids = request.POST.getlist("survey-response-ids", [])
        responses = SurveyResponse.objects.filter(id__in=survey_response_ids).order_by('library_name')
        filename = u"Exporterade enkätsvar ({})".format(strftime("%Y-%m-%d %H.%M.%S"))

        rows = [[unicode(observation._source_key) for observation in responses[0].observations]]
        for response in responses:
            rows.append([unicode(observation.value) for observation in response.observations])

        return ExcelResponse(rows, filename)


@permission_required('is_superuser', login_url='index')
def publish_survey_response(request, survey_response_id):
    try:
        survey_response = SurveyResponse.objects.get(pk=survey_response_id)
    except:
        raise Http404

    if request.method == "POST":
        try:
            survey_response.publish(user=request.user)
        except Exception as e:
            logger.error(u"Error when publishing survey response {}:".format(sr.id))
            print e

    return redirect("edit_survey_response", survey_response_id)


@permission_required('is_superuser', login_url='index')
def edit_survey_response(request, survey_response_id):
    try:
        survey_response = SurveyResponse.objects.get(pk=survey_response_id)
    except:
        raise Http404

    # Needed to render the other form in the view
    observations_form = SurveyObservationsForm(instance=survey_response)

    if request.method == "POST":
        form = SurveyResponseForm(request.POST, instance=survey_response)

        if form.is_valid():
            try:
                survey_response = form.save(user=request.user);
                return redirect("edit_survey_response", survey_response_id)

            except NotUniqueError as nue:
                logger.warning(u"A SurveyResponse with library_name {} already exists for year {}: {}".format(
                    survey_response.library_name, survey_response.sample_year, nue))
                form._errors['library_name'] = ErrorList([u"Det finns redan ett enkätsvar för detta bibliotek"])
            except Exception as e:
                logger.warning(u"Error updating SurveyResponse {}: {}".format(survey_response_id, e))
                form._errors['__all__'] = ErrorList([u"Kan inte uppdatera respondentinformation"])
        else:
            logger.debug(u"Form has validation errors: {}".format(form.errors))
    else:
        form = SurveyResponseForm(instance=survey_response)

    return _render_survey_response_view(request, form, observations_form)


def _render_survey_response_view(request, survey_response_form, survey_observations_form):
    context = {
        'form': survey_response_form,
        'observations_form': survey_observations_form,
    }
    return render(request, 'libstat/edit_survey_response.html', context)


@permission_required('is_superuser', login_url='index')
def edit_survey_observations(request, survey_response_id):
    """
        Handling saving of survey observations in a separate view method.
        Called from view edit_survey_response.
    """
    try:
        survey_response = SurveyResponse.objects.get(pk=survey_response_id)
    except:
        raise Http404

    if request.method == "POST":
        form = SurveyObservationsForm(request.POST, instance=survey_response)
        if form.is_valid():
            try:
                survey_response = form.save(user=request.user)
            except Exception as e:
                logger.warning(u"Error updating SurveyResponse observations {}: {}".format(survey_response_id, e))
                form._errors['__all__'] = ErrorList([u"Kan inte uppdatera enkätsvar"])
        else:
            logger.debug(u"Form has validation errors: {}".format(form.errors))
            return _render_survey_response_view(request, SurveyResponseForm(instance=survey_response), form)

    return redirect("edit_survey_response", survey_response_id)


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
    data = [v.as_simple_dict() for v in variables];
    return HttpResponse(json.dumps(data), content_type="application/json")


@permission_required('is_superuser', login_url='index')
def surveys(request):
    """
        List surveys view
    """
    surveys = Survey.objects.all()
    context = {
        'surveys': surveys,
    }
    return render(request, 'libstat/surveys.html', context)


@permission_required('is_superuser', login_url='index')
def create_survey(request):
    context = {
        'mode': 'create',
        'form_url': reverse("create_survey"),
    }

    if request.method == "POST":
        form = SurveyForm(request.POST)
        if form.is_valid():
            try:
                survey = form.save(user=request.user)
                return redirect("edit_survey", survey.id)
            except Exception as e:
                logger.warning(u"Error creating survey: {}".format(e))
                form._errors['__all__'] = ErrorList([u"Kan inte skapa enkät"])

    else:
        form = SurveyForm()

    context['form'] = form
    return render(request, 'libstat/edit_survey.html', context)


###############################
### Begin survey experiment ###
###############################

def cell(variable_key, sum_of=[], required=False, is_integer=True):
    variable = Variable.objects.get(key=variable_key)
    return {
        u"variable_key": variable_key,
        u"sum_of": " ".join(sum_of),
        u"required": required,
        u"is_integer": is_integer,
        u"main_label": variable.question,
        u"sub_label": variable.question_part,
        u"description": variable.description
    }


def row(description="", explanation="", cells=[]):
    return {
        u"description": description,
        u"explanation": explanation,
        u"cells": cells
    }


def group(rows, description="", columns=1, headers=[]):
    return {
        u"description": description,
        u"columns": columns,
        u"headers": headers,
        u"rows": rows
    }


survey_template = {
    u"key": "",
    u"target_year": "",
    u"organization_name": "",
    u"municipality": "",
    u"municipality_code": "",
    u"head_authority": "",
    u"respondent_name": "",
    u"respondent_email": "",
    u"respondent_phone": "",
    u"website": "",
    u"sections": [
        {
            u"title": u"Exempeltitel",
            u"groups": [
                group(
                    description="Beskrivning för gruppen",
                    columns=3,
                    headers=["Första kolumnen", "Andra kolumnen", "Tredje kolumnen"],
                    rows=[
                        row(
                            description="Lorem ipsum dolor sit amet, elit.",
                            explanation="Extra förklaring för rad ett.",
                            cells=[
                                cell(u"Folk1"),
                                cell(u"Folk2", required=True),
                                cell(u"Folk3", sum_of=[u"Folk1", u"Folk2"], is_integer=False)
                            ]

                        ),
                        row(
                            description="Lorem ipsum dolor sit amet, elit.",
                            explanation="Extra förklaring för rad två.",
                            cells=[
                                cell(u"Folk4"),
                                cell(u"Folk5", required=True),
                                cell(u"Folk6", sum_of=[u"Folk4", u"Folk5"], is_integer=False)
                            ]
                        )
                    ]
                )
            ]
        }
    ]
}


survey_dict = {
    u"key": u"abcdefgh",
    u"target_year": u"2014",
    u"organization_name": u"Karlstads stadsbibliotek",
    u"municipality": u"Karlstad",
    u"municipality_code": u"1780",
    u"head_authority": u"Kulturrådet i Karlstad",
    u"respondent_name": u"Helena Fernström",
    u"respondent_email": u"helena.fernström@bibliotek.karlstad.se",
    u"respondent_phone": u"054 - 64 82 09",
    u"website": u"www.bibliotek.karlstad.se",
    u"Folk1": 145,
    u"Folk2": 123,
    u"Folk3": 834,
    u"Folk4": 20,
    u"Folk5": 489,
    u"Folk6": u""
}


def cell_to_input_field(cell):
    attrs = {"class": "form-control"}
    if cell[u"sum_of"]:
        attrs["data-sum-of"] = cell[u"sum_of"]
    if cell[u"required"]:
        attrs["required"] = ""
    if cell[u"is_integer"]:
        attrs["data-is-integer"] = ""
    return forms.CharField(required=False, widget=forms.TextInput(attrs=attrs))


class SurveyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)
        observation = survey_dict
        for field in survey_template:
            if field == u"sections":
                self.sections = []
                for template_section in survey_template[u"sections"]:
                    section = {
                        u"title": template_section[u"title"],
                        u"groups": []
                    }
                    for template_group in template_section[u"groups"]:
                        group = {
                            u"description": template_group[u"description"],
                            u"headers": template_group[u"headers"],
                            u"columns": template_group[u"columns"],
                            u"rows": []
                        }
                        for template_row in template_group[u"rows"]:
                            row = {
                                u"cells": [],
                                u"description": template_row[u"description"],
                                u"explanation": template_row[u"explanation"]
                            }
                            for template_cell in template_row[u"cells"]:
                                key = template_cell[u"variable_key"]
                                self.fields[key] = cell_to_input_field(template_cell)
                                self.fields[key].initial = observation[key]
                                row[u"cells"].append(template_cell)
                            group[u"rows"].append(row)
                        section[u"groups"].append(group)
                    self.sections.append(section)
            elif field == u"target_year":
                self.target_year = observation[u"target_year"]
            elif field == u"key":
                self.fields[field] = forms.CharField(required=False, widget=forms.HiddenInput())
                self.fields[field].initial = observation[field]
            else:
                self.fields[field] = forms.CharField(required=False,
                                                     widget=forms.TextInput(attrs={"class": "form-control"}))
                self.fields[field].initial = observation[field]


@permission_required('is_superuser', login_url='index')
def edit_survey(request, survey_id):
    if request.method == "POST":
        form = SurveyForm(request.POST)
        if form.is_valid():
            for field in form.cleaned_data:
                survey_dict[field] = form.cleaned_data[field]

    context = {"form": SurveyForm()}
    return render(request, 'libstat/survey_template.html', context)


#############################
### End survey experiment ###
#############################


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
    data = [{'key': v.key, 'id': str(v.id)} for v in variables];
    return HttpResponse(json.dumps(data), content_type="application/json")
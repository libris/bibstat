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

from libstat.models import Observation
from libstat.forms import *
from libstat.apis import *
from libstat.survey_templates import survey_template


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
        'target_groups': target_groups
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
            rows.append(
                [observation.value if observation.value else "" for observation in response.observations])

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
            logger.error(u"Error when publishing survey response {}:".format(survey_response_id.id))
            print e

    return redirect("edit_survey", survey_response_id)


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


###############################
### Begin survey experiment ###
###############################

def survey_response_from_template(template, create_non_existing_variables=False):
    response = SurveyResponse(
        library_name=u"Motala stadsbibliotek",
        sample_year=2014,
        target_group="public",
        observations=[],
        metadata=SurveyResponseMetadata(
            municipality_name=u"Karlstad",
            municipality_code=u"1780",
        )
    )
    for section in template.sections:
        for group in section.groups:
            for row in group.rows:
                for cell in row.cells:
                    try:
                        v = Variable.objects.get(key=cell.variable_key)
                    except Exception:
                        if create_non_existing_variables:
                            v = Variable(
                                key=cell.variable_key,
                                description=u"",
                                is_public=False,
                                type=u"integer",
                                target_groups=["public", "research", "hospital", "school"]
                            )
                            v.save_updated_self_and_modified_replaced([])
                        else:
                            raise Exception(
                                "Can't create SurveyResponse with non-existing Variable " + cell.variable_key)
                    response.observations.append(SurveyObservation(variable=v))

    return response


def save_survey_from_form(survey_id, form):
    response = SurveyResponse.objects.get(pk=survey_id)
    if form.is_valid():
        disabled_inputs = form.cleaned_data["disabled_inputs"].split(" ")
        for field in form.cleaned_data:
            observation = response.get_observation(field)
            if observation:
                observation.value = form.cleaned_data[field]
                if field in disabled_inputs:
                    observation.disabled = True
            else:
                response.__dict__["_data"][field] = form.cleaned_data[field]
    response.save()

@permission_required('is_superuser', login_url='index')
def create_survey_response(request):
    try:
        survey_response_from_template(survey_template, create_non_existing_variables=True).save()
    except NotUniqueError:
        pass

    return index(request)


@permission_required('is_superuser', login_url='index')
def edit_survey(request, survey_id):
    if request.method == "POST":
        survey = SurveyResponse.objects.get(pk=survey_id)
        form = SurveyForm(request.POST, instance=survey)
        save_survey_from_form(survey_id, form)

    survey = SurveyResponse.objects.get(pk=survey_id)
    context = {"form": SurveyForm(instance=survey)}
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
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

from libstat.models import Section, Group, Cell, Row, SurveyTemplate, Observation, SurveyResponse_
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
            logger.error(u"Error when publishing survey response {}:".format(survey_response_id.id))
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

def cell(variable_key, types=[], sum_of=[], sum_siblings=[], required=False):
    return Cell(variable_key=variable_key,
                sum_of=sum_of,
                sum_siblings=sum_siblings,
                previous_value="",
                required=required,
                types=types)


survey_template = SurveyTemplate(
    key="",
    target_year="",
    organization_name="",
    municipality="",
    municipality_code="",
    head_authority="",
    respondent_name="",
    respondent_email="",
    respondent_phone="",
    website="",
    sections=[
        Section(
            title=u"Frågor om biblioteksorganisationen",
            groups=[
                Group(
                    description="",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="1. Vad heter du som fyller i enkäten?",
                            explanation="Kontaktuppgift, om vi har någon fråga om lämnade uppgifter.",
                            cells=[cell(u"Namn01", types=[])]
                        ),
                        Row(
                            description="2. Vad har du för e-postadress?",
                            explanation="Vi skickar länk till rapporten när den publiceras. E-postadressen valideras automatiskt så att du fyllt i en användbar e-postadress, det går därför inte att skriva två adresser i fältet.",
                            cells=[cell(u"Epost01", types=['email', 'required'])]
                        ),
                        Row(
                            description="3. Vänligen fyll i ditt telefonnummer, inklusive riktnummer.",
                            explanation="Används så att vi kan kontakta dig om vi har några frågor om de lämnade uppgifterna",
                            cells=[cell(u"Tele01", types=[])]
                        ),
                        Row(
                            description="4. Vänligen skriv in länk till en webbplats där vi kan nå den biblioteksplan eller annan plan som styr er verksamhet.",
                            explanation="",
                            cells=[cell(u"Plan01", types=[])]
                        )
                    ]
                ),
                # TODO Välja bibliotek (5)
                Group(
                    description="",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="6. Enkätens uppgifter avser totalt antal bemannade servicesställen:",
                            explanation="",
                            cells=[cell(u"BemanService01", types=['required', 'integer'])]
                        ),
                        Row(
                            description="7. Hur många av de bemannade serviceställena är integrerade bibliotek? Folk- och skolbibliotek alternativt forsknings- och sjukhusbibliotek alternativt folk- och forskningsbibliotek?",
                            explanation="",
                            cells=[cell(u"Integrerad01", types=['required', 'integer'])]
                        )
                    ]
                ),
                Group(
                    description="8. Till de bemannade servicesställen som den här enkäten avser är det kanske också kopplat ett antal obemannade utlåningsställen där vidare låneregistrering inte sker. Antal obemannade utlåningsställen och utlån till sådana:",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Antal obemannade utlåningsställen där vidare låneregistrering inte sker",
                            explanation="",
                            cells=[cell(u"Obeman01", types=['required', 'integer'])]
                        ),
                        Row(
                            description="Antal utlån till servicesställen/institutioner där vidare lånregistrering inte sker under kalenderåret (inkl. institutionslån och depositioner)",
                            explanation="",
                            cells=[cell(u"ObemanLan01", types=['required', 'integer'])]
                        )
                    ]
                ),
                Group(
                    description="9. Hur många bokbussar, bokbilar och bokbusshållplatser administrerar de uppräknade biblioteksenheterna? Om ni köper tjänsten av ett annat bibliotek som sköter administrationen uppge värdet 0 för att omöjliggöra dubbelräkning på riksnivå. Ange 0 om frågan inte är aktuell för er.",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Antal bokbussar",
                            explanation="",
                            cells=[cell(u"Bokbuss01", types=['required', 'integer'])]
                        ),
                        Row(
                            description="Antal bokbusshållplatser inom kommunen",
                            explanation="",
                            cells=[cell(u"BokbussHP01", types=['required', 'integer'])]
                        ),
                        Row(
                            description="Antal bokbilar, transportfordon",
                            explanation="",
                            cells=[cell(u"Bokbil01", types=['integer'])]
                        )
                    ]
                ),
                Group(
                    description="10. Antal personer som biblioteket förväntas betjäna. Exempelvis antal elever (skolbibliotek), antal anställda (myndighetsbibliotek), antal helårsekvivalenter (forskningsbibliotek). Uppgift om antal kommuninnevånare behöver inte lämnas av folkbibliotek.",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Antal personer",
                            explanation="",
                            cells=[cell(u"Population01", types=['integer'])]
                        )
                    ]
                ),
            ]
        ),
        Section(
            title=u"Frågor om biblioteksorganisationen", # Personkomm variabel för comment
            comment=u"Här kan du lämna eventuella kommentarer till frågeområdet personal. Vänligen skriv inga siffror här.",
            groups=[
                Group(
                    description="11. Hur många årsverken avsattes för biblioteksverksamheten under kalenderåret?",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Antal årsverken bibliotekarier och dokumentalister",
                            explanation="",
                            cells=[cell(u"Arsverke01", types=['integer'])]
                        ),
                        Row(
                            description="Antal årsverken biblioteksassistenter och lärarbibliotekarier",
                            explanation="",
                            cells=[cell(u"Arsverke02", types=['integer'])]
                        ),
                        Row(
                            description="Antal årsverken specialister inom IT, information eller ämnessakkunniga, fackkunniga",
                            explanation="",
                            cells=[cell(u"Arsverke03", types=['integer'])]
                        ),
                        Row(
                            description="Antal årsverken övrig personal inklusive kvällspersonal studentvakter, chaufförer, vaktmästare",
                            explanation="",
                            cells=[cell(u"Arsverke04", types=['integer'])]
                        ),
                        Row(
                            description="Totalt antal årsverken avsatt bemanning för biblioteksverksamhet",
                            explanation="",
                            cells=[cell(u"Arsverke99", types=['required', 'integer'])]
                        ),
                        Row(
                            description="- varav antal av dessa ovanstående årsverken var särskilt avsatta för barn och unga",
                            explanation="",
                            cells=[cell(u"Arsverke05", types=['required', 'integer'])]
                        )
                    ]
                ),
                Group(
                    description="12. Hur många personer arbetade inom biblioteksverksamheten 31 mars?",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Antal anställda kvinnor",
                            explanation="",
                            cells=[cell(u"Personer01", types=['sum'], sum_siblings=['Personer02'])]
                        ),
                        Row(
                            description="Antal anställda män",
                            explanation="",
                            cells=[cell(u"Personer02", types=['sum'], sum_siblings=['Personer01'])]
                        ),
                        Row(
                            description="Totalt antal anställda personer",
                            explanation="",
                            cells=[cell(u"Personer99", types=['sum'], sum_of=[u"Personer01", u"Personer02"])]
                        )
                    ]
                )
            ]
        ),
        Section(
            title=u"Frågor om ekonomi", # TODO Koppla comment till Ekonomikomm
            comment=u"Här kan du lämna eventuella kommentarer till frågeområdet ekonomi. Vänligen skriv inga siffror här.",
            groups=[
                Group(
                    description="13. Vilka utgifter hade biblioteksverksamheten under kalenderåret? Antal hela kronor inklusive mervärdesskatt. Avrunda inte till tusental. Vänligen skriv uppgifterna utan punkt, mellanslag eller kommatecken.",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Inköp av tryckta medier och audiovisuella medier",
                            explanation="",
                            cells=[cell(u"Utgift01", types=['sum'], sum_siblings=[u"Utgift02",u"Utgift03",u"Utgift04",u"Utgift05",u"Utgift06"])]
                        ),
                        Row(
                            description="Inköp av virtuella e-baserade media och databaslicenser (exklusive kostnader för biblioteksdatasystemet)",
                            explanation="",
                            cells=[cell(u"Utgift02", types=['sum'], sum_siblings=[u"Utgift01",u"Utgift03",u"Utgift04",u"Utgift05",u"Utgift06"])]
                        ),
                        Row(
                            description="Lönekostnader personal",
                            explanation="",
                            cells=[cell(u"Utgift03", types=['sum'], sum_siblings=[u"Utgift01",u"Utgift02",u"Utgift04",u"Utgift05",u"Utgift06"])]
                        ),
                        Row(
                            description="Kostnader för personalens kompetensutveckling",
                            explanation="",
                            cells=[cell(u"Utgift04", types=['sum'], sum_siblings=[u"Utgift01",u"Utgift02",u"Utgift03",u"Utgift05",u"Utgift06"])]
                        ),
                        Row(
                            description="Lokalkostnader",
                            explanation="",
                            cells=[cell(u"Utgift05", types=['sum'], sum_siblings=[u"Utgift01",u"Utgift02",u"Utgift03",u"Utgift04",u"Utgift06"])]
                        ),
                        Row(
                            description="Övriga driftskostnader som inte ingår i punkterna ovan (inklusive kostnader för bibliotekssystemet)",
                            explanation="",
                            cells=[cell(u"Utgift06", types=['sum'], sum_siblings=[u"Utgift01",u"Utgift02",u"Utgift03",u"Utgift04",u"Utgift05"])]
                        ),
                        Row(
                            description="Totala driftskostnader för biblioteksverksamheten (summan av ovanstående)",
                            explanation="",
                            cells=[cell(u"Utgift99", types=['sum'], sum_of=[u"Utgift01",u"Utgift02",u"Utgift03",u"Utgift04",u"Utgift05",u"Utgift06"])]
                        ),
                        Row(
                            description="Investeringsutgifter, inklusive kapitalkostnader för dessa",
                            explanation="",
                            cells=[cell(u"Utgift07", types=['integer'])]
                        )
                    ]
                ),
                Group(
                    description="14. Vilka egengenererade intäkter hade biblioteksverksamheten? Antal hela kronor. Avrunda inte till tusental.",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Projektmedel som inte kommer från huvudmannen eller moderorganisationen samt sponsring och gåvor",
                            explanation="",
                            cells=[cell(u"Intakt01", types=['sum'], sum_siblings=[u"Intakt02",u"Intakt03"])]
                        ),
                        Row(
                            description="Försäljning av bibliotekstjänster och personalresurser till andra huvudmän, organisationer och företag",
                            explanation="",
                            cells=[cell(u"Intakt02", types=['sum'], sum_siblings=[u"Intakt01",u"Intakt03"])]
                        ),
                        Row(
                            description="Försenings- och reservationsutgifter eller intäkter av uthyrningsverksamhet samt försäljning av böcker och profilprodukter",
                            explanation="",
                            cells=[cell(u"Intakt03", types=['sum'], sum_siblings=[u"Intakt01",u"Intakt02"])]
                        ),
                        Row(
                            description="Totalt antal kronor egengenererade inkomster",
                            explanation="",
                            cells=[cell(u"Intakt99", types=['sum'], sum_of=[u"Intakt01",u"Intakt02",u"Intakt03"])]
                        ),
                    ]
                )
            ]
        ),
        Section(
            title=u"Bestånd – nyförvärv",
            comment=u"",
            groups=[
                Group(
                    description="15. Hur stort var det fysiska mediebeståndet och det elektroniska titelbeståndet 31 december och hur många fysiska nyförvärv gjordes under kalenderåret uppdelat på olika medietyper? Om ni bara kan få fram fysiskt bestånd genom att räkna hyllmeter, använd omräkningstal 40 medier per hyllmeter om ni beräknar antal utifrån uppgift om hyllmeter.",
                    columns=3,
                    headers=[],
                    rows=[]
                )
            ]
        ),
    ]
)

survey_response = SurveyResponse_(
    key=u"abcdefgh",
    target_year=u"2014",
    organization_name=u"Karlstads stadsbibliotek",
    municipality=u"Karlstad",
    municipality_code=u"1780",
    head_authority=u"Kulturrådet i Karlstad",
    respondent_name=u"Helena Fernström",
    respondent_email=u"helena.fernström@bibliotek.karlstad.se",
    respondent_phone=u"054 - 64 82 09",
    website=u"www.bibliotek.karlstad.se",
    observations=[
        Observation(variable_key=u"Namn01", value="1", disabled=False),
        Observation(variable_key=u"Epost01", value="a@a.se", disabled=False),
        Observation(variable_key=u"Tele01", value="1", disabled=False),
        Observation(variable_key=u"Plan01", value="1", disabled=False),
        Observation(variable_key=u"BemanService01", value="1", disabled=False),
        Observation(variable_key=u"Integrerad01", value="1", disabled=False),
        Observation(variable_key=u"Obeman01", value="1", disabled=False),
        Observation(variable_key=u"ObemanLan01", value="1", disabled=False),
        Observation(variable_key=u"Bokbuss01", value="1", disabled=False),
        Observation(variable_key=u"BokbussHP01", value="1", disabled=False),
        Observation(variable_key=u"Bokbil01", value="1", disabled=False),
        Observation(variable_key=u"Population01", value="1", disabled=False),
        Observation(variable_key=u"Arsverke01", value="1", disabled=False),
        Observation(variable_key=u"Arsverke02", value="1", disabled=False),
        Observation(variable_key=u"Arsverke03", value="1", disabled=False),
        Observation(variable_key=u"Arsverke04", value="1", disabled=False),
        Observation(variable_key=u"Arsverke99", value="1", disabled=False),
        Observation(variable_key=u"Arsverke05", value="1", disabled=False),
        Observation(variable_key=u"Personer01", value="1", disabled=False),
        Observation(variable_key=u"Personer02", value="1", disabled=False),
        Observation(variable_key=u"Personer99", value="1", disabled=False),
        Observation(variable_key=u"Utgift01", value="1", disabled=False),
        Observation(variable_key=u"Utgift02", value="1", disabled=False),
        Observation(variable_key=u"Utgift03", value="1", disabled=False),
        Observation(variable_key=u"Utgift04", value="1", disabled=False),
        Observation(variable_key=u"Utgift05", value="1", disabled=False),
        Observation(variable_key=u"Utgift06", value="1", disabled=False),
        Observation(variable_key=u"Utgift99", value="1", disabled=False),
        Observation(variable_key=u"Utgift07", value="1", disabled=False),
        Observation(variable_key=u"Intakt01", value="1", disabled=False),
        Observation(variable_key=u"Intakt02", value="1", disabled=False),
        Observation(variable_key=u"Intakt03", value="1", disabled=False),
        Observation(variable_key=u"Intakt99", value="1", disabled=False),
    ])


def cell_to_input_field(cell, observation):
    attrs = {"class": "form-control",
             "id": cell.variable_key,
             "name": cell.variable_key}

    if "sum" in cell.types:
        attrs["data-bv-integer"] = ""
        attrs["data-bv-greaterthan"] = ""
        attrs["data-bv-greaterthan-value"] = "0"
        attrs["data-bv-greaterthan-inclusive"] = ""
        attrs["data-bv-notempty"] = ""
        if cell.sum_of:
            attrs["data-sum-of"] = " ".join(map(lambda s: s, cell.sum_of))
        if cell.sum_siblings:
            attrs["data-sum-siblings"] = " ".join(map(lambda s: s, cell.sum_siblings))

    if "required" in cell.types:
        attrs["data-bv-notempty"] = ""

    if "integer" in cell.types:
        attrs["data-bv-integer"] = ""
        attrs["data-bv-greaterthan"] = ""
        attrs["data-bv-greaterthan-value"] = "0"
        attrs["data-bv-greaterthan-inclusive"] = ""

    if "email" in cell.types:
        attrs["data-bv-emailaddress"] = ""

    if observation.disabled:
        attrs["disabled"] = ""

    field = forms.CharField(required=False, widget=forms.TextInput(attrs=attrs))
    field.initial = observation.value
    return field


class SurveyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)
        response = survey_response

        self.fields["key"] = forms.CharField(required=False, widget=forms.HiddenInput())
        self.fields["organization_name"] = forms.CharField(required=False,
                                                           widget=forms.TextInput(attrs={"class": "form-control",
                                                                                         "disabled": ""}))
        self.fields["municipality"] = forms.CharField(required=False,
                                                      widget=forms.TextInput(attrs={"class": "form-control",
                                                                                    "disabled": ""}))
        self.fields["municipality_code"] = forms.CharField(required=False,
                                                           widget=forms.TextInput(attrs={"class": "form-control",
                                                                                         "disabled": ""}))
        self.fields["head_authority"] = forms.CharField(required=False,
                                                        widget=forms.TextInput(attrs={"class": "form-control",
                                                                                      "disabled": ""}))
        self.fields["respondent_name"] = forms.CharField(required=False,
                                                         widget=forms.TextInput(attrs={"class": "form-control"}))
        self.fields["respondent_email"] = forms.CharField(required=False,
                                                          widget=forms.TextInput(attrs={"class": "form-control"}))
        self.fields["respondent_phone"] = forms.CharField(required=False,
                                                          widget=forms.TextInput(attrs={"class": "form-control"}))
        self.fields["website"] = forms.CharField(required=False,
                                                 widget=forms.TextInput(attrs={"class": "form-control"}))

        self.fields["key"].initial = response.key
        self.fields["organization_name"].initial = response.organization_name
        self.fields["municipality"].initial = response.municipality
        self.fields["municipality_code"].initial = response.municipality_code
        self.fields["head_authority"].initial = response.head_authority
        self.fields["respondent_name"].initial = response.respondent_name
        self.fields["respondent_email"].initial = response.respondent_email
        self.fields["respondent_phone"].initial = response.respondent_phone
        self.fields["website"].initial = response.website

        self.target_year = response.target_year
        self.sections = survey_template.sections
        for section in survey_template.sections:
            for group in section.groups:
                for row in group.rows:
                    for cell in row.cells:
                        variable_key = cell.variable_key
                        observation = response.get_observation(variable_key)
                        self.fields[variable_key] = cell_to_input_field(cell, observation)


@permission_required('is_superuser', login_url='index')
def edit_survey(request, survey_id):
    if request.method == "POST":
        form = SurveyForm(request.POST)
        response = survey_response
        if form.is_valid():
            for field in form.cleaned_data:
                observation = response.get_observation(field)
                if observation:
                    observation.value = form.cleaned_data[field]
                    if form.cleaned_data[field] == "Värdet är okänt":
                        observation.disabled = True
                    else:
                        observation.disabled = False
                else:
                    response.__dict__["_data"][field] = form.cleaned_data[field]

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
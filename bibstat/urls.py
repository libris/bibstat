import django_js_reverse
from django.conf.urls import url
from django.urls import reverse, path, re_path
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth import logout

from django_js_reverse.views import urls_js

from django.contrib import admin
import libstat
from libstat.apis.open_data import data_api, observation_api, export_api
from libstat.apis.terms import term_api, terms_api

from libstat.views.auth import login
from libstat.views.administration import administration, create_new_collection
from libstat.views.articles import article, articles, articles_delete
from libstat.views.dispatches import dispatches, dispatches_delete, dispatches_send
from libstat.views.index import index
from libstat.views.reports import reports, report
from libstat.views.surveys import (surveys,
                                   surveys_statuses,
                                   surveys_export,
                                   surveys_export_with_previous,
                                   surveys_activate,
                                   surveys_inactivate,
                                   surveys_overview,
                                   import_and_create,
                                   remove_empty,
                                   match_libraries,
                                   surveys_update_library)
from libstat.views.survey import (survey,
                                  survey_status,
                                  survey_notes,
                                  example_survey,
                                  sigel_survey,
                                  release_survey_lock)
from libstat.views.variables import (variables,
                                     edit_variable,
                                     create_variable, replaceable_variables)

urlpatterns = [
    re_path(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name="robots"),
    re_path(r'^humans\.txt$', TemplateView.as_view(template_name='humans.txt', content_type='text/plain; charset=utf-8'), name="humans"),

    # APIs
    re_path(r'^data$', data_api, name="data_api"),
    re_path(r'^data/(?P<observation_id>\w+)$', observation_api, name="observation_api"),
    re_path(r'^def/terms$', terms_api, name="terms_api"),
    re_path(r'^def/terms/(?P<term_key>\w+)$', term_api, name="term_api"),
    re_path(r'^export$', export_api, name='export_api'),

    # Auth
    re_path(r'^login$', login, name='login'),
    re_path(r'^logout$', logout, {'next_page': 'admin'}, name='logout'),

    # Index
    re_path(r'^$', index, name='index'),
    re_path(r'^admin$', libstat.views.index.admin, name='admin'),

    # Articles
    re_path(r'^article/(?P<article_id>\w+)$', article, name='article'),
    re_path(r'^article$', article, name='article'),
    re_path(r'^articles$', articles, name='articles'),
    re_path(r'^articles/delete/(?P<article_id>\w+)$', articles_delete, name='articles_delete'),

    # Reports
    re_path(r'^reports$', reports, name='reports'),
    re_path(r'^report$', report, name='report'),

    # Administration
    re_path(r'^administration/create_new_collection$', create_new_collection, name='create_new_collection'),
    #re_path(r'^administration$', administration, name='administration'),

    # Survey
    re_path(r'^surveys$', surveys, name='surveys'),
    re_path(r'^surveys/example$', example_survey, name='example_survey'),
    re_path(r'^surveys/activate$', surveys_activate, name='surveys_activate'),
    re_path(r'^surveys/inactivate$', surveys_inactivate, name='surveys_inactivate'),
    re_path(r'^surveys/export$', surveys_export, name='surveys_export'),
    re_path(r'^surveys/export_with_previous$', surveys_export_with_previous, name='surveys_export_with_previous'),
    re_path(r'^surveys/import_and_create$', import_and_create, name='surveys_import_and_create'),
    re_path(r'^surveys/remove_empty$', remove_empty, name='surveys_remove_empty'),
    re_path(r'^surveys/match_libraries$', match_libraries, name='surveys_match_libraries'),
    re_path(r'^surveys/status$', surveys_statuses, name='surveys_statuses'),
    re_path(r'^surveys/overview/(?P<sample_year>\w+)$', surveys_overview, name='surveys_overview'),
    re_path(r'^surveys/status/(?P<survey_id>\w+)$', survey_status, name='survey_status'),
    re_path(r'^surveys/notes/(?P<survey_id>\w+)$', survey_notes, name='survey_notes'),
    re_path(r'^surveys/update_library$', surveys_update_library, name='surveys_update_library'),
    re_path(r'^surveys/sigel/(?P<sigel>\w+)$', sigel_survey, name='sigel_survey'),
    re_path(r'^surveys/unlock/(?P<survey_id>\w+)$', release_survey_lock, name='release_survey_lock'),
    re_path(r'^surveys/(?P<survey_id>\w+)$', survey, name='survey'),

    # Dispatch
    re_path(r'^dispatches$', dispatches, name='dispatches'),
    re_path(r'^dispatches/delete$', dispatches_delete, name='dispatches_delete'),
    re_path(r'^dispatches/send', dispatches_send, name='dispatches_send'),

    # Variables
    re_path(r'^variables$', variables, name='variables'),
    re_path(r'^variables/new$', create_variable, name='create_variable'),
    re_path(r'^variables/replaceable$', replaceable_variables, name='replaceable_variables'),
    re_path(r'^variables/(?P<variable_id>\w+)$', edit_variable, name='edit_variable'),

    # Other
    #re_path(r'^.well-known/void$', RedirectView.as_view(url=reverse('open_data'), permanent=False)),
    re_path(r'^jsreverse/$', urls_js, name='js_reverse'),
]


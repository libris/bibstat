from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.contrib.auth.views import logout

from django.contrib import admin

from libstat.views.apis import (data_api,
                                term_api,
                                terms_api,
                                observation_api,
                                open_data)
from libstat.views.auth import login
from libstat.views.administration import administration, create_new_collection
from libstat.views.articles import articles
from libstat.views.dispatches import dispatches, dispatches_delete, dispatches_send
from libstat.views.index import index
from libstat.views.surveys import (surveys_statuses,
                                   surveys_export,
                                   surveys_active,
                                   surveys_inactive,
                                   surveys_activate,
                                   surveys_inactivate,
                                   surveys_overview,
                                   import_and_create)
from libstat.views.survey import (survey,
                                  survey_status,
                                  survey_notes)
from libstat.views.variables import (variables,
                                     edit_variable,
                                     create_variable)

admin.autodiscover()

urlpatterns = patterns(
    '',

    # APIs
    url(r'^open_data$', open_data, name="open_data"),
    url(r'^data$', data_api, name="data_api"),
    url(r'^data/(?P<observation_id>\w+)$', observation_api, name="observation_api"),
    url(r'^def/terms$', terms_api, name="terms_api"),
    url(r'^def/terms/(?P<term_key>\w+)$', term_api, name="term_api"),

    # Auth
    url(r'^login', login, name='login'),
    url(r'^logout', logout, {'next_page': 'index'}, name='logout'),

    # Index
    url(r'^$', index, name='index'),

    # Articles
    url(r'^articles', articles, name='articles'),

    # Administration
    url(r'^administration/create_new_collection', create_new_collection, name='create_new_collection'),
    url(r'^administration', administration, name='administration'),

    # Survey
    url(r'^surveys$', surveys_active, name='surveys'),
    url(r'^surveys/active$', surveys_active, name='surveys_active'),
    url(r'^surveys/inactive$', surveys_inactive, name='surveys_inactive'),
    url(r'^surveys/activate$', surveys_activate, name='surveys_activate'),
    url(r'^surveys/inactivate$', surveys_inactivate, name='surveys_inactivate'),
    url(r'^surveys/export$', surveys_export, name='surveys_export'),
    url(r'^surveys/import_and_create$', import_and_create, name='surveys_import_and_create'),
    url(r'^surveys/status$', surveys_statuses, name='surveys_statuses'),
    url(r'^surveys/overview/(?P<sample_year>\w+)$', surveys_overview, name='surveys_overview'),
    url(r'^surveys/status/(?P<survey_id>\w+)$', survey_status, name='survey_status'),
    url(r'^surveys/notes/(?P<survey_id>\w+)$', survey_notes, name='survey_notes'),
    url(r'^surveys/(?P<survey_id>\w+)$', survey, name='survey'),

    # Dispatch
    url(r'^dispatches$', dispatches, name='dispatches'),
    url(r'^dispatches/delete$', dispatches_delete, name='dispatches_delete'),
    url(r'^dispatches/send', dispatches_send, name='dispatches_send'),

    # Variables
    url(r'^variables$', variables, name='variables'),
    url(r'^variables/new$', create_variable, name='create_variable'),
    url(r'^variables/(?P<variable_id>\w+)$', edit_variable, name='edit_variable'),

    # Other
    url(r'^.well-known/void$', RedirectView.as_view(url=reverse_lazy('open_data'),
                                                    permanent=False)),
    url(r'^jsreverse/$', 'django_js_reverse.views.urls_js', name='js_reverse')
)

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
from libstat.views.helpers import (replaceable_variables_api,
                                   surveyable_variables_api)
from libstat.views.dispatches import dispatches, dispatches_delete, dispatches_send
from libstat.views.index import index
from libstat.views.surveys import (surveys_statuses,
                                   surveys_export,
                                   surveys_publish,
                                   surveys,
                                   surveys_remove,
                                   surveys_overview)
from libstat.views.survey import (survey,
                                  survey_status)
from libstat.views.libraries import (libraries,
                                     import_libraries,
                                     remove_libraries)
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

    # Helpers
    url(r'^variables/replaceable$', replaceable_variables_api, name='replaceable_variables_api'),
    url(r'^variables/surveyable$', surveyable_variables_api, name='surveyable_variables_api'),

    # Index
    url(r'^$', index, name='index'),

    # Survey
    url(r'^surveys$', surveys, name='surveys'),
    url(r'^surveys/export$', surveys_export, name='surveys_export'),
    url(r'^surveys/publish$', surveys_publish, name='surveys_publish'),
    url(r'^surveys/remove$', surveys_remove, name='surveys_remove'),
    url(r'^surveys/status$', surveys_statuses, name='surveys_statuses'),
    url(r'^surveys/overview/(?P<sample_year>\w+)$', surveys_overview, name='surveys_overview'),
    url(r'^surveys/status/(?P<survey_id>\w+)$', survey_status, name='survey_status'),
    url(r'^surveys/(?P<survey_id>\w+)$', survey, name='survey'),

    # Dispatch
    url(r'^dispatches$', dispatches, name='dispatches'),
    url(r'^dispatches/delete$', dispatches_delete, name='dispatches_delete'),
    url(r'^dispatches/send', dispatches_send, name='dispatches_send'),

    # Variables
    url(r'^variables$', variables, name='variables'),
    url(r'^variables/new$', create_variable, name='create_variable'),
    url(r'^variables/(?P<variable_id>\w+)$', edit_variable, name='edit_variable'),

    # Libraries
    url(r'^libraries$', libraries, name='libraries'),
    url(r'^libraries/import$', import_libraries, name='import_libraries'),
    url(r'^libraries/remove$', remove_libraries, name='remove_libraries'),

    # Other
    url(r'^.well-known/void$', RedirectView.as_view(url=reverse_lazy('open_data'),
                                                    permanent=False)),
    url(r'^jsreverse/$', 'django_js_reverse.views.urls_js', name='js_reverse')
)

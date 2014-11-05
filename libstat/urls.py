# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.views import logout

from libstat.views import (open_data,
                           data_api,
                           observation_api,
                           terms_api,
                           term_api,
                           login,
                           replaceable_variables_api,
                           surveyable_variables_api,
                           index,
                           surveys,
                           survey,
                           surveys_publish,
                           surveys_export,
                           variables,
                           create_variable,
                           edit_variable,
                           libraries,
                           surveys_status,
                           import_libraries,
                           remove_libraries,
                           surveys_remove,
                           dispatches,
                           dispatches_delete,
                           dispatches_send,
                           surveys_overview)


urlpatterns = patterns(
    'libstat.views',

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
    url(r'^surveys/overview/(?P<sample_year>\w+)$', surveys_overview, name='surveys_overview'),
    url(r'^surveys/status/(?P<survey_id>\w+)$', surveys_status, name='surveys_status'),
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
    url(r'^libraries/remove$', remove_libraries, name='remove_libraries')
)

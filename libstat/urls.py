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
                           survey_responses,
                           clean_example_surveys,
                           edit_survey,
                           publish_survey_responses,
                           publish_survey_response,
                           export_survey_responses,
                           variables,
                           create_variable,
                           edit_variable,
                           libraries,
                           edit_survey_status,
                           import_libraries,
                           remove_libraries)


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
    url(r'^surveys$', survey_responses, name='survey_responses'),
    url(r'^surveys/clean_example_surveys$', clean_example_surveys, name='clean_example_surveys'),
    url(r'^surveys/edit/(?P<survey_id>\w+)$', edit_survey, name='edit_survey'),
    url(r'^surveys/edit/status/(?P<survey_id>\w+)$', edit_survey_status, name='edit_survey_status'),
    url(r'^surveys/publish$', publish_survey_responses, name='publish_survey_responses'),
    url(r'^surveys/publish/(?P<survey_response_id>\w+)$', publish_survey_response, name='publish_survey_response'),
    url(r'^surveys/export$', export_survey_responses, name='export_survey_responses'),

    # Variables
    url(r'^variables$', variables, name='variables'),
    url(r'^variables/new$', create_variable, name='create_variable'),
    url(r'^variables/(?P<variable_id>\w+)$', edit_variable, name='edit_variable'),

    # Libraries
    url(r'^libraries$', libraries, name='libraries'),
    url(r'^libraries/import$', import_libraries, name='import_libraries'),
    url(r'^libraries/remove$', remove_libraries, name='remove_libraries')
)

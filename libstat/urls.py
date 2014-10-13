# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.views import logout

from libstat import views


urlpatterns = patterns('libstat.views',
                       # Public views
                       url(r'^$', views.index, name='index'),
                       url(r'^open_data/$', views.open_data, name="open_data"),

                       # Open API views
                       url(r'^data/$', views.data_api, name="data_api"),
                       url(r'^data/(?P<observation_id>\w+)/$', views.observation_api, name="observation_api"),
                       url(r'^def/terms/$', views.terms_api, name="terms_api"),
                       url(r'^def/terms/(?P<term_key>\w+)/$', views.term_api, name="term_api"),

                       # Login
                       url(r'^login', views.login, name='login'),
                       url(r'^logout', logout, {'next_page': 'index'}, name='logout'),

                       # Admin views
                       url(r'^variables/$', views.variables, name='variables'),
                       url(r'^variables/new/$', views.create_variable, name='create_variable'),
                       url(r'^variables/(?P<variable_id>\w+)/$', views.edit_variable, name='edit_variable'),
                       url(r'^surveys/$', views.surveys, name='surveys'),
                       url(r'^surveys/new$', views.create_survey, name='create_survey'),
                       url(r'^surveys/(?P<survey_id>\w+)/$', views.edit_survey, name='edit_survey'),
                       url(r'^survey_responses/$', views.survey_responses, name='survey_responses'),
                       url(r'^survey_responses/publish$', views.publish_survey_responses,
                           name='publish_survey_responses'),
                       url(r'^survey_responses/export$', views.export_survey_responses, name='export_survey_responses'),
                       url(r'^survey_responses/(?P<survey_response_id>\w+)/$', views.edit_survey_response,
                           name='edit_survey_response'),
                       url(r'^survey_responses/(?P<survey_response_id>\w+)/observations/$',
                           views.edit_survey_observations, name='edit_survey_observations'),
                       url(r'^survey_responses/(?P<survey_response_id>\w+)/publish/$', views.publish_survey_response,
                           name='publish_survey_response'),

                       # Admin helper APIs
                       url(r'^variables/replaceable$', views.replaceable_variables_api,
                           name='replaceable_variables_api'),
                       url(r'^variables/surveyable$', views.surveyable_variables_api, name='surveyable_variables_api'),
)
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from libstat import views
from django.contrib.auth.views import login, logout

urlpatterns = patterns('libstat.views',
    # Public views
    url(r'^$',views.index, name='index'),
    url(r'^open_data/$', views.open_data, name="open_data"),

    # API views
    url(r'^data/$', views.data_api, name="data_api"),
    url(r'^data/(?P<observation_id>\w+)/$', views.observation_api, name="observation_api"),
    url(r'^def/terms/$', views.terms_api, name="terms_api"),
    url(r'^def/terms/(?P<term_key>\w+)/$', views.term_api, name="term_api"),
    
    # Login 
    url(r'^login', login, {'template_name': 'libstat/login.html'}, name='login'),
    url(r'^logout', logout, {'next_page': 'index'}, name='logout'),
    
    # Admin views
    url(r'^variables/$',views.variables, name='variables'),
    #url(r'^variables/(?P<variable_id>\w+)/$',views.variable_detail, name='variable_detail'),
    url(r'^variables/(?P<variable_id>\w+)/$',views.edit_variable, name='edit_variable'),
    url(r'^survey_responses/$',views.survey_responses, name='survey_responses'),
    url(r'^survey_responses/publish$',views.publish_survey_responses, name='publish_survey_responses'),
)
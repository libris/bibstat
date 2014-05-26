# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from libstat import views

urlpatterns = patterns('libstat.views',
    url(r'^$',views.index, name='index'),
    url(r'^open_data/$', views.open_data, name="open_data"),
    
    url(r'^variables/$',views.variables, name='variables'),
    url(r'^variables/(?P<variable_id>\w+)/$',views.variable_detail, name='variable_detail'),
    
    url(r'^survey_responses/$',views.survey_responses, name='survey_responses'),
)
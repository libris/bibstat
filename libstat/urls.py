# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from libstat import views
from django.contrib.auth.views import login, logout

urlpatterns = patterns('libstat.views',
    # Public views
    url(r'^$',views.index, name='index'),
    url(r'^open_data/$', views.open_data, name="open_data"),

    # API views
    url(r'^data/$', views.data, name="data"),
    url(r'^def/terms', views.terms, name="terms"),
    
    # Login 
    url(r'^login', login, {'template_name': 'libstat/login.html'}, name='login'),
    url(r'^logout', logout, {'next_page': 'index'}, name='logout'),
    
    # Admin views
    url(r'^variables/$',views.variables, name='variables'),
    url(r'^variables/(?P<variable_id>\w+)/$',views.variable_detail, name='variable_detail'),
    
    url(r'^survey_responses/$',views.survey_responses, name='survey_responses'),
    
    
)
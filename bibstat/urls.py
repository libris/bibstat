from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bibstat.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^statistics/', include('libstat.urls')),
    url(r'^$', 'libstat.views.index')
)

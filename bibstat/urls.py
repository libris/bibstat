from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bibstat.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # TODO: Fix a login page and remove otherwise unused and broken admin site
    url(r'^admin/', include(admin.site.urls)),

    # Mongonaut MongoDB admin GUI. 
    # NOTE: Mongonaut does not have a login form but views requires authentication!
    url(r'^mongonaut/', include('mongonaut.urls')),
)

from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bibstat.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^statistics/', include('libstat.urls')),
    url(r'^$', 'libstat.views.index'),
    url(r'^.well-known/void$',
        RedirectView.as_view(url=reverse_lazy('open_data'), permanent=False))
)

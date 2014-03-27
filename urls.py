from django.contrib import admin
admin.autodiscover()

from django.conf.urls import patterns, include, url
from .apps.toplevel.views import homepage


urlpatterns = patterns('',
    url(r"^$", homepage),
    url(r"^home$", homepage),
    url(r"^projects/gel2", include("agendr.apps.gel2.urls")),
    url(r"^projects/htdistribution", include("agendr.apps.htdistribution.urls")),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r"^accounts/login/$", "django.contrib.auth.views.login"),
)


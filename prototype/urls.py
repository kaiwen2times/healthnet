from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'prototype.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^', include('healthnet.urls', namespace="healthnet")),
    url(r'^admin/', include(admin.site.urls)),
)

"""
Definition of urls for cfgmgmtcenter.
"""

from rest_framework.authtoken import views
from datetime import datetime
from django.conf.urls import patterns, url, include

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Rest API authentication
    url(r'^api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Token Infra
    url(r'^api/token/', views.obtain_auth_token),

    # Apps WebUI and API
    url(r'^api/', include('api.urls')),
    url(r'^', include('webui.urls')),

    # Admin Site
    url(r'^admin/', include(admin.site.urls)),
)

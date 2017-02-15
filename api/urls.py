# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from api import views, signals
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)

router.register(r'application', views.ApplicationViewSet)
router.register(r'department', views.DepartmentViewSet)
router.register(r'environment', views.EnvironmentViewSet)
router.register(r'templatetag', views.TemplateTagViewSet)
router.register(r'applicationtag', views.ApplicationTagViewSet)
router.register(r'tagvalue', views.TagValueViewSet)
router.register(r'package', views.PackageViewSet)

urlpatterns = router.urls
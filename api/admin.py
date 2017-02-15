# -*- coding: utf-8 -*-

from django.contrib import admin
from api import models
from simple_history.admin import SimpleHistoryAdmin
from guardian.admin import GuardedModelAdmin


# REF
# http://stackoverflow.com/questions/10928860/objects-with-permissions-assigned-by-django-guardian-not-visible-in-admin

class ApplicationAdmin(SimpleHistoryAdmin, GuardedModelAdmin):

    def queryset(self, request):        
        return models.Application.objects.all()

class DepartmentAdmin(SimpleHistoryAdmin, GuardedModelAdmin):

    def queryset(self, request):
        return models.Department.objects.all()

class EnvironmentAdmin(SimpleHistoryAdmin, GuardedModelAdmin):
    
    def queryset(self, request):
        return models.Environment.objects.all()

class TemplateTagAdmin(SimpleHistoryAdmin, GuardedModelAdmin):

    def queryset(self, request):
        return models.TemplateTag.objects.all()

class TagValueAdmin(SimpleHistoryAdmin, GuardedModelAdmin):

    def queryset(self, request):
        return models.TagValue.objects.all()

class PackageAdmin(SimpleHistoryAdmin, GuardedModelAdmin):

    def queryset(self, request):
        return models.Package.objects.all()

class ApplicationTagAdmin(SimpleHistoryAdmin, GuardedModelAdmin):

    def queryset(self, request):
        return models.ApplicationTag.objects.all()

admin.site.register(models.Application, ApplicationAdmin)
admin.site.register(models.Department, DepartmentAdmin)
admin.site.register(models.Environment, EnvironmentAdmin)
admin.site.register(models.TemplateTag, TemplateTagAdmin)
admin.site.register(models.ApplicationTag, ApplicationTagAdmin)
admin.site.register(models.TagValue, TagValueAdmin)
admin.site.register(models.Package, PackageAdmin)
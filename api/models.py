# -*- coding: utf-8 -*-

from django.db import models
from common.models import UniqueNameDescModel, NameModel, NameDescModel, CommonModel
from simple_history.models import HistoricalRecords
from fernet_fields import EncryptedCharField
from textwrap import wrap


class Application(UniqueNameDescModel):

    history = HistoricalRecords()

    class Meta:
        permissions = (
            ('view_application', 'Can view application'),
        )
        ordering = ['name', ]

class Department(UniqueNameDescModel):
    
    applications = models.ManyToManyField(Application)
    history = HistoricalRecords()

    class Meta:
        permissions = (
            ('view_department', 'Can view department'),
        )
        ordering = ['name', ]

class Environment(UniqueNameDescModel):
    
    history = HistoricalRecords()

    class Meta:
        permissions = (
            ('view_environment', 'Can view environment'),
        )
        ordering = ['name', ]

class TemplateTag(UniqueNameDescModel):

    history = HistoricalRecords()
    
    class Meta:
        permissions = (
            ('view_templatetag', 'Can view template tag'),
        )
        ordering = ['name', ]

    def __unicode__(self):
        return self.name

class ApplicationTag(CommonModel):
    application = models.ForeignKey(Application)
    file_path = models.CharField(max_length=255)
    tags = models.ManyToManyField(TemplateTag)
    history = HistoricalRecords()

    class Meta:
        unique_together = (("application", "file_path"), )
        permissions = (
            ('view_applicationtag', 'Can view application tag'),
        )

    def __unicode__(self):
        name = '{0}_{1}'.format(self.application.name, self.file_path)
        if len(name) > 20:
            name = '{0} ...'.format(wrap(name, width=20)[0])
        return name

class TagValue(CommonModel):
    environment = models.ForeignKey(Environment)
    tag = models.ForeignKey(TemplateTag)
    value = EncryptedCharField(max_length=1024)
    history = HistoricalRecords()

    class Meta:
        unique_together = (("environment", "tag"), )
        permissions = (
            ('view_tagvalue', 'Can view tag value'),
        )
        ordering = ['tag__name', ]

    def __unicode__(self):
        if len(self.value) > 20:
            name = u'{0} ...'.format(wrap(self.value, width=20)[0])
        else:
            name = u'{0}'.format(self.value)
        return name

class Package(NameDescModel):

    platforms = (
        ('Windows', 'Windows'),
        ('Linux', 'Linux'),
    )

    application = models.ForeignKey(Application)
    environment = models.ForeignKey(Environment)
    target_platform = models.CharField(choices=platforms, default="Windows", max_length=10)
    branch_name = models.CharField(default="master", max_length=40)
    output_path = models.CharField(max_length=255)
    status = models.CharField(max_length=255, default="", null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        permissions = (
            ('view_package', 'Can view package'),
        )
        ordering = ['-created_date', ]

    def __unicode__(self):
        return self.name


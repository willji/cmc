# -*- coding: utf-8 -*-

from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
from django.http import HttpResponseRedirect
from api import models, tasks
from guardian.shortcuts import assign_perm, remove_perm
from django.db.models.query_utils import Q
from guardian.models import UserObjectPermission, GroupObjectPermission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from webui.utilities import ConfigurationHelper


# REF
# https://snakeycode.wordpress.com/2014/10/17/django-signals-example/
# http://www.cnblogs.com/esperyong/archive/2012/12/21/2827841.html

#region django guardian permissions

@receiver(post_save, sender=models.Application)
def assign_application_perm(sender, **kwargs):
    instance = kwargs['instance']

    # assign test and ops view_department permission
    opsGroup, created = Group.objects.get_or_create(name='ops')
    assign_perm('view_application', opsGroup, instance)
    testGroup, created = Group.objects.get_or_create(name='test')
    assign_perm('view_application', testGroup, instance)

    if not instance.creator.is_superuser:
        depaGroup, created = Group.objects.get_or_create(name=instance.creator.groups.all()[0])
        assign_perm('view_application', depaGroup, instance)

@receiver(post_save, sender=models.Application)
def update_department_apps(sender, **kwargs):
    instance = kwargs['instance']

    # add application to creator's department
    creatorGroup = instance.creator.groups.all()[0]
    department = models.Department.objects.get(name=creatorGroup.name)
    department.applications.add(instance)
    department.save()

@receiver(pre_delete, sender=models.Application)
def remove_application_perm(sender, instance, **kwargs):
    filters = Q(content_type=ContentType.objects.get_for_model(instance),
        object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()

@receiver(post_save, sender=models.Department)
def assign_department_perm(sender, **kwargs):
    instance = kwargs['instance']

    # assign test and ops view_department permission
    opsGroup, created = Group.objects.get_or_create(name='ops')
    assign_perm('view_department', opsGroup, instance)
    testGroup, created = Group.objects.get_or_create(name='test')
    assign_perm('view_department', testGroup, instance)

    # instance.name should be a department name
    # all group members in that group should have update permission
    depaGroup, created = Group.objects.get_or_create(name=instance.name)
    assign_perm('view_department', depaGroup, instance)

    # grant add, change, delete permissions to one department(group), but the department(group) cannot delete the department itself.
    permissions = Permission.objects.filter(
        Q(content_type__app_label='api') & ~Q(content_type__model__iendswith='package') & ~Q(content_type__model__iendswith='environment')).filter(
             Q(codename__istartswith='add') | Q(codename__istartswith='change') | Q(codename__istartswith='delete') | Q(codename='view_templatetag')).exclude(
                Q(codename='delete_department') | Q(codename='delete_templatetag'))
    for permission in permissions:
        depaGroup.permissions.add(permission)

@receiver(pre_delete, sender=models.Department)
def remove_department_perm(sender, instance, **kwargs):
    filters = Q(content_type=ContentType.objects.get_for_model(instance),
        object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()

    # remove department group
    Group.objects.filter(name=instance.name).delete()

@receiver(post_save, sender=models.Environment)
def assign_environment_perm(sender, **kwargs):
    instance = kwargs['instance']

    # assign test and ops view_department permission
    opsGroup, created = Group.objects.get_or_create(name='ops')
    assign_perm('view_environment', opsGroup, instance)
    testGroup, created = Group.objects.get_or_create(name='test')
    assign_perm('view_environment', testGroup, instance)

    # environment does not need to assign permission for creator's group

@receiver(pre_delete, sender=models.Environment)
def remove_environment_perm(sender, instance, **kwargs):
    filters = Q(content_type=ContentType.objects.get_for_model(instance),
        object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()

@receiver(post_save, sender=models.TemplateTag)
def assign_templatetag_perm(sender, **kwargs):
    instance = kwargs['instance']

    # assign test and ops view_applicationtag permission
    opsGroup, created = Group.objects.get_or_create(name='ops')
    assign_perm('view_templatetag', opsGroup, instance)
    testGroup, created = Group.objects.get_or_create(name='test')
    assign_perm('view_templatetag', testGroup, instance)

    if not instance.creator.is_superuser:
        depaGroup, created = Group.objects.get_or_create(name=instance.creator.groups.all()[0])
        assign_perm('change_templatetag', depaGroup, instance)

@receiver(pre_delete, sender=models.TemplateTag)
def remove_templatetag_perm(sender, instance, **kwargs):
    filters = Q(content_type=ContentType.objects.get_for_model(instance),
        object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()

@receiver(post_save, sender=models.ApplicationTag)
def assign_applicationtag_perm(sender, **kwargs):
    instance = kwargs['instance']

    # assign test and ops view_applicationtag permission
    opsGroup, created = Group.objects.get_or_create(name='ops')
    assign_perm('view_applicationtag', opsGroup, instance)
    testGroup, created = Group.objects.get_or_create(name='test')
    assign_perm('view_applicationtag', testGroup, instance)

    if not instance.creator.is_superuser:
        depaGroup, created = Group.objects.get_or_create(name=instance.creator.groups.all()[0])
        assign_perm('view_applicationtag', depaGroup, instance)

@receiver(pre_delete, sender=models.ApplicationTag)
def remove_applicationtag_perm(sender, instance, **kwargs):
    filters = Q(content_type=ContentType.objects.get_for_model(instance),
        object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()

@receiver(post_save, sender=models.TagValue)
def assign_tagvalue_perm(sender, **kwargs):
    instance = kwargs['instance']

    # all groups can see tag values,
    # only ops team and creator's group can see tag values for production.
    # test team can update non-prod tag values.
    # only creator's group can delete tag values that created by that group.
    if instance.environment.name != settings.PROD_ENV_NAME:
        for group in Group.objects.all():
            assign_perm('view_tagvalue', group, instance)
        testGroup, created = Group.objects.get_or_create(name='test')
        assign_perm('change_tagvalue', testGroup, instance)
    else:
        opsGroup, created = Group.objects.get_or_create(name='ops')
        assign_perm('view_tagvalue', opsGroup, instance)

        creatorGroup = instance.creator.groups.all()[0]
        assign_perm('view_tagvalue', creatorGroup, instance)

    creatorGroup = instance.creator.groups.all()[0]
    assign_perm('change_tagvalue', creatorGroup, instance)
    assign_perm('delete_tagvalue', creatorGroup, instance)

@receiver(pre_delete, sender=models.TagValue)
def remove_tagvalue_perm(sender, instance, **kwargs):
    filters = Q(content_type=ContentType.objects.get_for_model(instance),
        object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()

#endregion

#region Other actions

@receiver(post_save, sender=models.Package)
def build_config_package(sender, **kwargs):
    instance = kwargs['instance']

    # Using django-celery to download files asynchronously.
    tasks.build_cfgpackage.delay(instance)

#endregion
# -*- coding: utf-8 -*-

from celery import shared_task
from api import models
from webui.utilities import ConfigurationHelper


@shared_task
def build_cfgpackage(instance):

    try:
        helper = ConfigurationHelper()

        appDepartment = None
        for department in models.Department.objects.all():
            if department.applications.filter(name=instance.application.name):
                appDepartment = department
                break

        models.Package.objects.filter(pk=instance.id).update(status=u'正在打包')
        helper.download_file(instance)        
        helper.parse_file(instance)
        helper.package_file(instance)
        helper.upload_file(instance)
        models.Package.objects.filter(pk=instance.id).update(status=u'完成')
        return instance
    except Exception as e:
        if e.message:
            models.Package.objects.filter(pk=instance.id).update(status=e.message)
        else:
            models.Package.objects.filter(pk=instance.id).update(status=u'打包失败，请直接再试一次')
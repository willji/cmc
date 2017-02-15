# encoding: utf-8

from __future__ import absolute_import
from celery import Celery
from django.conf import settings
from datetime import timedelta
import os

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfgmgmtcenter.settings')

app = Celery('cfgmgmtcenter')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
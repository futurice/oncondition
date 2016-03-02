from __future__ import absolute_import
from django.conf import settings
import os
from celery import Celery

app = Celery('test')
app.config_from_object(os.getenv("CELERY_CONFIG_MODULE", 'test.celeryconfig'))
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

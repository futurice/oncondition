# -*- coding: utf-8 -*-
from django.apps import apps
from django.conf import settings
from django.db import models

class Sample(models.Model):
    name = models.CharField(max_length=255)

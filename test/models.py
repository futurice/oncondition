# -*- coding: utf-8 -*-
from django.apps import apps
from django.conf import settings
from django.db import models

from djangodirtyfield.mixin import DirtyFieldMixin

class Sample(models.Model):
    name = models.CharField(max_length=255)

class Person(models.Model, DirtyFieldMixin):
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)

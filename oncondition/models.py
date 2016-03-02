# -*- coding: utf-8 -*-
from django.apps import apps
from django.core.cache import cache
from django.conf import settings
from django.db import models
from django.db.models import Count

from oncondition.events import CACHE_KEY

class Event(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, unique=True)
    cls = models.CharField(max_length=255)
    model = models.CharField(max_length=255, db_index=True)
    waiting = models.BooleanField(default=False)
    recipients = models.CharField(max_length=255, blank=True, null=True)

    @classmethod
    def models_with_events(self):
        result = cache.get(CACHE_KEY)
        if result is None:
            result = [k['model'] for k in self.objects.values('model').annotate(cnt=Count('id'))]
            cache.set(CACHE_KEY, result)
        return [apps.get_model(m) for m in result]

    def __unicode__(self):
        return self.name

class EventWaiting(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey('oncondition.Event', null=True, blank=True, on_delete=models.SET_NULL)
    uid = models.PositiveIntegerField()
    processed = models.BooleanField(default=False, db_index=True)

    def __unicode__(self):
        return u"(%s, %s)"%(self.event_id, self.uid)

    class Meta:
        unique_together = (('event', 'uid'),)


# -*- coding: utf-8 -*-
from django.apps import apps
from django.core.cache import cache
from django.conf import settings
from django.db import models, ProgrammingError
from django.db.models import Count

from oncondition.events import CACHE_KEY, event_waiting_model

class Event(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, unique=True)
    cls = models.CharField(max_length=255)
    model = models.CharField(max_length=255, db_index=True)
    recipients = models.CharField(max_length=255, blank=True, null=True)

    @classmethod
    def models_with_events(self):
        result = cache.get(CACHE_KEY)
        if result is None:
            try:
                result = [k['model'] for k in self.objects.values('model').annotate(cnt=Count('id'))]
                cache.set(CACHE_KEY, result)
            except ProgrammingError: # post_save and initial migrations
                result = []
        return [apps.get_model(m) for m in result]

    def __unicode__(self):
        return self.name

class EventWaiting(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey('oncondition.Event',
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
            related_name="waitings")
    uid = models.PositiveIntegerField()
    conditions = models.CharField(max_length=255, null=True, blank=True)
    processed = models.BooleanField(default=False, db_index=True)

    def get_conditions(self):
        return filter(None, map(lambda s: s.strip(), self.conditions.split(','))) if self.conditions else []

    def __unicode__(self):
        return u"(%s, %s)"%(self.event_id, self.uid)

    class Meta:
        unique_together = (('event', 'uid'),)


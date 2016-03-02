from __future__ import absolute_import
from django.apps import apps
from django.conf import settings
from django.template.loader import render_to_string

import os, logging

from oncondition.util import import_string, email

logger = logging.getLogger('events')

CACHE_KEY = "oncondition-models"

def event_model():
    return apps.get_model(os.getenv("ET_MODEL", 'oncondition.Event'))

def event_waiting_model():
    return apps.get_model(os.getenv("ET_WAITMODEL", 'oncondition.EventWaiting'))

def trigger_events(instance, changes, events=[], waiting=False):
    for event in events:
        ev = import_string(event.cls)
        ev_instance = ev(
                event=event,
                instance=instance,
                changes=changes,
                waiting=waiting)
        ctx = ev_instance.condition(instance, changes)
        if ctx:
            ev_instance.action(instance, context=ctx)
            # also set related delayed events as processed to avoid duplicate actions
            delayed_events = event_waiting_model().objects.filter(event_id=event.pk, uid=instance.pk)
            if delayed_events and not delayed_events[0].processed:
                delayed_events.update(processed=True)
        logger.debug("{} / waiting {} | {}".format(ev, bool(waiting), bool(ctx)))

def trigger_event(instance, changes, event):
    trigger_events(instance, changes, [event])

def trigger_timed_event(instance, waiting):
    trigger_events(instance, {}, [waiting.event], waiting=waiting)

class Event(object):
    def __init__(self, event, instance, changes={}, waiting=None):
        self.event = event
        self.instance = instance
        self.changes = changes
        self.waiting = waiting

    def condition(self, instance, context):
        # True/False, or [[a],[b],[c], ...]/[] when a condition ignites multiple events
        raise Exception("condition missing")

    def action(self, instance, context):
        raise Exception("event missing")

    def to_as_str(self, to):
        to = [to] if not isinstance(to, list) else to
        return ', '.join(to)

    def recipients(self):
        return (self.event.recipients or '').split(',')

    def mail(self, subject, body, to, attachments=[], *args, **kwargs):
        email(subject=subject, body=body, to=to, attachments=attachments)

    def log(self, event):
        logger.debug(event)


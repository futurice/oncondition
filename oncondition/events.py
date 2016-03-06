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
        success, ctxs = ev_instance.on_conditions(instance, changes)
        if success:
            ev_instance.success(instance, ctxs)
        else:
            ev_instance.failure(instance, ctxs)
        logger.debug("{}: {}".format(ev, success))

def trigger_event(instance, changes, event):
    trigger_events(instance, changes, [event])

def trigger_timed_event(instance, waiting):
    trigger_events(instance, {}, [waiting.event], waiting=waiting)

class Event(object):
    def __init__(self, event, instance, changes={}, waiting=None, **kw):
        self.event = event
        self.instance = instance
        self.changes = changes
        self.waiting = waiting
        self.kw = kw

    def success(self, instance, ctxs):
        self.action(instance, context=ctxs)
        # set related delayed events as processed to avoid duplicate actions
        delayed_events = event_waiting_model().objects.filter(event_id=self.event.pk, uid=instance.pk)
        if delayed_events and not delayed_events[0].processed:
            delayed_events.update(processed=True)

    def failure(self, instance, ctxs):
        for cond, ctx in ctxs.iteritems():
            if (bool(ctx) is False) and hasattr(self, "%s_failure"%cond):
                fail_fn = getattr(self, "%s_failure"%cond)
                fail_fn(instance, ctx)

    def conditions(self):
        return ['condition', 'time_condition',]

    def _conditions(self):
        conditions = self.conditions()
        if self.waiting:
            conditions = self.waiting.get_conditions() or conditions
        return conditions

    def on_conditions(self, instance, context):
        """
        Returns:
            tuple: A tuple of (bool, dict) containing (success, contexts) of each condition.
                   Contexts contain {conditionName: context}, where context is Nothing (False),
                   or Something (True). """
        ctxs = {cond: getattr(self, cond)(instance, context) for cond in self._conditions()}
        return (all(ctxs.values()), ctxs)

    def time_condition_failure(self, instance, context, name='my-timed-event', conditions=None):
        event = event_model().objects.get(name=name)
        event_waiting_model().objects.get_or_create(event=event,
                                                    uid=instance.pk,
                                                    conditions=conditions,)

    def time_condition(self, instance, context):
        return True

    def condition(self, instance, context):
        raise Exception("Event.condition() undefined")

    def action(self, instance, context):
        raise Exception("Event.action() undefined")

    def to_as_str(self, to):
        to = [to] if not isinstance(to, list) else to
        return ', '.join(to)

    def recipients(self):
        return (self.event.recipients or '').split(',')

    def mail(self, subject, body, to, attachments=[], *args, **kwargs):
        email(subject=subject, body=body, to=to, attachments=attachments)

    def log(self, event):
        logger.debug(event)

class TimedEvent(Event):
    pass

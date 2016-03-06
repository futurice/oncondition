# -*- coding: utf-8 -*-
import os

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from django.test import TestCase, TransactionTestCase, override_settings
from django.test.client import Client
from django.contrib.auth.models import Group, User

from oncondition.events import Event, event_model, event_waiting_model
from oncondition.tasks import handle_timed_events

from djangodirtyfield.mixin import changed
from .models import Person

import logging
logging.basicConfig(level=logging.DEBUG)

class BaseSuite(TransactionTestCase):
    pass

MAILS = []
LOGS = []
CONDITIONS_PROCESSED = []
SUCCESS = None

class LoggingEvent(Event):
    def success(self, instance, ctxs):
        global CONDITIONS_PROCESSED, SUCCESS
        CONDITIONS_PROCESSED = dict(ctxs)
        SUCCESS = True
        super(LoggingEvent, self).success(instance=instance, ctxs=ctxs)

    def failure(self, instance, ctxs):
        global CONDITIONS_PROCESSED, SUCCESS
        CONDITIONS_PROCESSED = dict(ctxs)
        SUCCESS = False
        super(LoggingEvent, self).failure(instance=instance, ctxs=ctxs)

    def mail(self, subject, body, to):
        MAILS.append([subject, body, to])

    def log(self, event):
        LOGS.append(event)

    def action(self, instance, context):
        self.mail(subject='Hello', body="body", to=self.recipients())
        self.log("Event")

class SampleEvent(LoggingEvent):
    def condition(self, instance, changes):
        return True

    def action(self, instance, context):
        self.mail(subject='Hello World', body="body", to=self.recipients())
        self.log("Sample Event")

class SampleTimedEvent(LoggingEvent):

    def time_condition_failure(self, instance, context, name="user-time-created", conditions=None):
        super(SampleTimedEvent, self).time_condition_failure(instance=instance, context=context, name=name, conditions=conditions)

    def time_condition(self, instance, changes):
        return False

    def condition(self, instance, changes):
        return True

    def action(self, instance, context):
        self.mail(subject='Hello Again', body="body", to=self.recipients())
        self.log("Timed Event")

class SampleTimedWithConditionsEvent(SampleTimedEvent):
    """ An Event where time_condition_failure sets up different conditions """
    def conditions(self):
        return ['condition','blocker_condition', 'time_condition',]

    def blocker_condition(self, instance, changes):
        return False

    def time_condition(self, instance, changes):
        return False

    def time_condition_failure(self, instance, context, name="user-time-created-blocker", conditions="condition, time_condition"):
        super(SampleTimedWithConditionsEvent, self).time_condition_failure(instance=instance,
                context=context,
                name=name,
                conditions=conditions)

class SampleMultiConditionsEvent(LoggingEvent):
    def conditions(self):
        return ['condition', 'time_condition', 'weather_condition', 'moon_phase_condition',]

    def condition(self, instance, changes):
        return True

    def time_condition(self, instance, changes):
        return True

    def weather_condition(self, instance, changes):
        return True

    def moon_phase_condition(self, instance, changes):
        return True

class SampleMultiConditionsOneFalseEvent(SampleMultiConditionsEvent):
    def weather_condition(self, instance, changes):
        return False

class DirtyEvent(LoggingEvent):
    def condition(self, instance, changes):
        return changed(changes, 'username')

    def action(self, instance, context):
        self.log("Username changed")

class EventTest(BaseSuite):
    def tearDown(self):
        global MAILS, LOGS, CONDITIONS_PROCESSED
        MAILS = []
        LOGS = []
        CONDITIONS_PROCESSED = []
        SUCCESS = None

    def test_form_fills_event(self):
        ev = event_model()
        ev.objects.get_or_create(name="user-created", cls="test.test_events.SampleEvent",model="auth.User")
        user = User.objects.create(first_name="F", last_name="L")
        self.assertEqual(len(MAILS), 1)
        self.assertEqual(LOGS[0], "Sample Event")

    def test_timed_event(self):
        ev = event_model()
        name = "user-time-created"
        ev.objects.get_or_create(name=name, cls="test.test_events.SampleTimedEvent", model="auth.User")
        self.assertEqual(len(LOGS), 0)
        user = User.objects.create(first_name="F", last_name="L")

        self.assertEqual(event_waiting_model().objects.filter(processed=False).count(), 1)
        self.assertEqual(ev.objects.get(name=name).waitings.count(), 1)
        self.assertEqual(len(LOGS), 0)

        def time_condition(self, instance, changes):
            return True
        orig_time_condition = SampleTimedEvent.time_condition
        SampleTimedEvent.time_condition = time_condition

        user.save()

        self.assertEqual(MAILS[0][0], "Hello Again")
        self.assertEqual(LOGS[0], "Timed Event")
        self.assertEqual(event_waiting_model().objects.filter(processed=False).count(), 0)
        self.assertEqual(ev.objects.get(name=name).waitings.count(), 1)
        self.assertEqual(list(ev.objects.get(name=name).waitings.filter(processed=False)), [])

        SampleTimedEvent.time_condition = orig_time_condition

    def test_timed_event_conditions(self):
        ev = event_model()
        name = "user-time-created-blocker"
        ev.objects.get_or_create(name=name, cls="test.test_events.SampleTimedWithConditionsEvent", model="auth.User")
        self.assertEqual(len(LOGS), 0)
        user = User.objects.create(first_name="F", last_name="L")

        self.assertEqual(event_waiting_model().objects.filter(processed=False).count(), 1)
        self.assertEqual(ev.objects.get(name=name).waitings.count(), 1)
        self.assertEqual(len(LOGS), 0)

        def time_condition(self, instance, changes):
            return True
        orig_time_condition = SampleTimedEvent.time_condition
        SampleTimedWithConditionsEvent.time_condition = time_condition

        # request doesnt processed Waiting's
        user.save()

        self.assertEqual(len(LOGS), 0)
        self.assertEqual(event_waiting_model().objects.filter(processed=False).count(), 1)

        # process Waitings'
        handle_timed_events.delay()

        self.assertEqual(len(LOGS), 1)
        self.assertEqual(event_waiting_model().objects.filter(processed=False).count(), 0)

        SampleTimedWithConditionsEvent.time_condition = orig_time_condition

    def test_timed_event_via_task(self):
        self.assertEqual(event_waiting_model().objects.all().count(), 0)
        ev = event_model()
        name = "user-time-created"
        ev.objects.get_or_create(name=name, cls="test.test_events.SampleTimedEvent", model="auth.User")
        self.assertEqual(len(LOGS), 0)
        user = User.objects.create(first_name="F", last_name="L")

        self.assertEqual(event_waiting_model().objects.filter(processed=False).count(), 1)
        self.assertEqual(ev.objects.get(name=name).waitings.count(), 1)
        self.assertEqual(len(LOGS), 0)

        def time_condition(self, instance, changes):
            return True
        orig_time_condition = SampleTimedEvent.time_condition
        SampleTimedEvent.time_condition = time_condition

        handle_timed_events.delay()

        self.assertEqual(MAILS[0][0], "Hello Again")
        self.assertEqual(LOGS[0], "Timed Event")
        self.assertEqual(event_waiting_model().objects.filter(processed=False).count(), 0)
        self.assertEqual(ev.objects.get(name=name).waitings.count(), 1)
        self.assertEqual(list(ev.objects.get(name=name).waitings.filter(processed=False)), [])

        SampleTimedEvent.time_condition = orig_time_condition

    def test_multi_condition_event(self):
        ev = event_model()
        ev.objects.get_or_create(name="manyconds", cls="test.test_events.SampleMultiConditionsEvent",model="auth.User")

        user = User.objects.create(first_name="F", last_name="L")
        self.assertEqual(len(CONDITIONS_PROCESSED), 4)
        self.assertEqual(SUCCESS, True)

    def test_multi_condition_one_false_event(self):
        ev = event_model()
        ev.objects.get_or_create(name="manyconds-onefalse", cls="test.test_events.SampleMultiConditionsOneFalseEvent",model="auth.User")

        user = User.objects.create(first_name="F", last_name="L")
        self.assertEqual(len(CONDITIONS_PROCESSED), 4)
        self.assertEqual(SUCCESS, False)

    def test_dirtyfield_integration(self):
        ev = event_model()
        ev.objects.get_or_create(name="username-changed", cls="test.test_events.DirtyEvent", model="test.Person")
        person = Person.objects.create(name="John W")
        self.assertEqual(len(LOGS), 0)
        person.username = "jow"
        person.save()
        self.assertEqual(LOGS[0], "Username changed")
        person.age = 17
        person.save()
        self.assertEqual(len(LOGS), 1)
        person.username = "johnw"
        person.save()
        self.assertEqual(len(LOGS), 2)



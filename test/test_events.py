# -*- coding: utf-8 -*-
import os

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase, TransactionTestCase, override_settings
from django.test.client import Client
from django.contrib.auth.models import Group, User

from oncondition.events import Event, event_model, event_waiting_model

import logging
logging.basicConfig(level=logging.DEBUG)

class BaseSuite(TransactionTestCase):
    pass

class SampleEvent(Event):
    def condition(self, instance, changes):
        return True

    def action(self, instance, context):
        self.mail(subject='Hello World', body="body", to=self.recipients())
        self.log("Sample Event! [%s]"%self.to_as_str(self.recipients()))

class EventTest(BaseSuite):
    def test_form_fills_event(self):
        ev = event_model()
        ev.objects.get_or_create(name="user-created", cls="test.test_events.SampleEvent",model="auth.User")
        user = User.objects.create(first_name="F", last_name="L")



# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_save

from oncondition.tasks import handle_events
from oncondition.events import event_model, CACHE_KEY

DIRTY = getattr(settings, 'DIRTYFIELDS_ENABLED', True)
from djangodirtyfield.mixin import DirtyFieldMixin

def on_post_save(sender, instance, created, **kwargs):
    if sender in event_model().models_with_events():
        handle_events.delay(label=instance._meta.label,
                pk=instance.id,
                changes=instance.get_dirtyfields_copy() if (DIRTY and isinstance(instance, DirtyFieldMixin)) else {})

def on_event_save(sender, instance, created, **kwargs):
    cache.delete(CACHE_KEY)

post_save.connect(on_post_save)
post_save.connect(on_event_save, sender=event_model())

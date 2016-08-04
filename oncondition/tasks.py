from __future__ import absolute_import
from django.apps import apps
from django.core import management
from django.core.exceptions import ObjectDoesNotExist

from oncondition.events import trigger_events, trigger_timed_event, event_model, event_waiting_model
from oncondition.util import import_string, celery_installation

app = celery_installation()

@app.task
def handle_events(label, pk, changes):
    events = event_model().objects.filter(model=label)
    model = apps.get_model(label)
    trigger_events(instance=model.objects.get(pk=pk), changes=changes, events=events)

@app.task
def handle_timed_events():
    waiting_model = event_waiting_model()
    for ev in waiting_model.objects.filter(processed=False):
        model = apps.get_model(ev.event.model)
        try:
            instance = model.objects.get(pk=ev.uid)
        except ObjectDoesNotExist as e:
            ev.update(processed=True)
            continue
        trigger_timed_event(instance=instance, waiting=ev)



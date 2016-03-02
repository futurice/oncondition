from __future__ import absolute_import
from django.apps import apps
from django.core import management

from oncondition.events import trigger_events, trigger_timed_event, event_model, event_waiting_model
from oncondition.util import import_string, celery_installation

app = celery_installation()

@app.task
def handle_events(label, pk, changes):
    event = event_model()
    events = filter(lambda e: not e.waiting, event.objects.filter(model=label))
    model = apps.get_model(label)
    trigger_events(instance=model.objects.get(pk=pk), changes=changes, events=events)

@app.task
def handle_timed_events():
    waiting_model = event_waiting_model()
    for ev in waiting_model.objects.filter(processed=False):
        model = apps.get_model(ev.event.model)
        trigger_timed_event(instance=model.objects.get(pk=ev.uid),
                            waiting=ev)

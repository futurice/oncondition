On Condition [![Build Status](https://travis-ci.org/futurice/oncondition.svg?branch=master)](https://travis-ci.org/futurice/oncondition)
============

Run actions based on conditions.

Why?
----

To provide transparency into 'What happens When?' and 'Is This working?' when bundling arbitrary logic into your application.
For example creating email notifications based on the form filledness criterias is a good use-case.

Environment Settings
--------------------
```
CELERY_MODULE = "foo.app"
```

Optional Environment Settings
-----------------------------
```
ET_MODEL = "oncondition.Event"
ET_WAITMODEL = "oncondition.EventWaiting"
```

Usage
-----

An Event, that fires when any User has changes:

```
from oncondition.events import Event
class MyEvent(Event):
    def condition(self, instance, changes):
        return 5>4

    def action(self, instance, context):
        self.mail(subject='[EVENT] Breakthrough!', body="--", to=self.recipients())
        self.log("My Event fired! Recipients: [%s]"%self.recipients())
```

Register the Event:

```
from oncondition.events import event_model
event_model().objects.get_or_create(name="my-event", cls="project.MyEvent", model="auth.User", recipients="me@company.com,you@company.com")
```

Delayed Events
--------------

On Condition supports any number of CONDITION_NAME -methods to run for a single Event, with their respective (optional) 'CONDITION_NAME_failure' -methods.
Out of the box ```time_condition``` has a respective ```time_condition_failure```, that created an EventWaiting -instance. This
allows to poll changes to an Event out of a request/response cycle. When the time_condition is met, it is marked as done.

Project integration and testing
-------------------------------

To test against Celery, provide your own CELERY_CONFIG_MODULE (see app_test_runner.py), eg:
```
# manage.py
    if 'test' in sys.argv:
        os.environ["CELERY_CONFIG_MODULE"] = "foo.tests.celeryconfig"
# foo.tests.celeryconfig
from foo.celeryconfig import *
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
```

Best practices
--------------
Extend oncondition.models.Event and point ```ET_MODEL```, ```ET_WAITMODEL``` to these.



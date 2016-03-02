On Condition
====================

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



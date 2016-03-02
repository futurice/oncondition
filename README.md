On Condition
====================

Run actions based on conditions.

Supports time-based delayed actions.

Why?
----

To provide transparency into 'What happens When?' and 'Is This working?', when bundling arbitrary logic into your application.

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



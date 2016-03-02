from django.core.mail import EmailMessage

import os, importlib

def import_string(dotted_path):
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except (ValueError, AttributeError) as e:
        module_path = dotted_path
    try:
        return importlib.import_module(dotted_path)
    except ImportError, e:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

def email(to, subject, body, attachments=[]):
    to = [to] if not isinstance(to, list) else to
    mail = EmailMessage(subject=subject, body=body, to=to)
    for attachment in attachments:
        mail.attach(*attachment)
    mail.send(fail_silently=False)

def celery_installation():
    """ Import Celery(), eg. foo.app """
    module = os.getenv("CELERY_MODULE", "")
    base = ".".join(module.split('.')[:-1])
    name = module.split('.')[-1]
    return getattr(import_string(base), name)


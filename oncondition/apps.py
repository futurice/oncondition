from django.apps import AppConfig

class EventAppConfig(AppConfig):
    name = 'oncondition'
    def ready(self):
        from oncondition import signals



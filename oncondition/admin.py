from django.conf import settings
from django.contrib import admin

from oncondition.models import Event, EventWaiting

class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'cls', 'model',]

class EventWaitingAdmin(admin.ModelAdmin):
    list_display = ['event', 'processed',]

admin.site.register(Event, EventAdmin)
admin.site.register(EventWaiting, EventWaitingAdmin)

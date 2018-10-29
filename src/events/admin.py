from django.contrib import admin
from events.models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_start_utc', 'event_end_utc', 'timezone']


admin.site.register(Event, EventAdmin)

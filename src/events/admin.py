from django.contrib import admin
from events.models import Event
from salads.admin import SaladInline
from django.utils.safestring import mark_safe
from salads.models import SaladFeedback


class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_start_utc', 'event_end_utc', 'timezone']
    inlines = [SaladInline]

    readonly_fields = ['label_link', 'salad_link', 'hash_id']

    @mark_safe
    def label_link(self, instance):
        return '<a href="{}" target="_blank">Download Label</a>'.format(instance.label_url)

    label_link.allow_tags = True

    @mark_safe
    def salad_link(self, instance):
        return '<a href="{}" target="_blank">Salad Link</a>'.format(instance.salad_url)

    label_link.allow_tags = True

    def hash_id(self, instance):
        return instance.hashed_id


admin.site.register(Event, EventAdmin)
admin.site.register(SaladFeedback)

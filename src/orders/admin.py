from django.contrib import admin
from orders.models import Order
from salads.admin import SaladInline
from django.utils.safestring import mark_safe


class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer']
    inlines = [SaladInline]

    readonly_fields = ['label_link']

    @mark_safe
    def label_link(self, instance):
        return '<a href="{}" target="_blank">Download Label</a>'.format(instance.label_url)

    label_link.allow_tags = True


admin.site.register(Order, OrderAdmin)

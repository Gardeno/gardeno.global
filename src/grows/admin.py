from django.contrib.gis import admin
from .models import Grow, Rack, Tray, TrayPosition, Sensor, GrowSensorPreferences, SensorSetupToken, SensorUpdate, \
    SensorAuthenticationToken, SensorRelay, RelaySchedule, RelayScheduleItem, SensorSwitch


class SensorSetupTokenAdmin(admin.ModelAdmin):
    readonly_fields = ['date_created']
    list_display = ['date_created', 'identifier', 'sensor', 'date_last_downloaded']


class SensorAuthenticationTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'date_created', 'date_deactivated', 'sensor', 'date_last_used']


class SensorRelayAdmin(admin.ModelAdmin):
    list_display = ['identifier', 'sensor', 'name', 'pin', 'date_created']


class RelayScheduleItemInline(admin.TabularInline):
    model = RelayScheduleItem
    extra = 0
    readonly_fields = ['date_created', 'is_new_schedule', 'date_scheduled', 'job_id', 'date_cancelled',
                       'date_completed', 'date_failed', 'failure_text']


class RelayScheduleAdmin(admin.ModelAdmin):
    inlines = (RelayScheduleItemInline,)


class SensorSwitchAdmin(admin.ModelAdmin):
    list_display = ['identifier', 'sensor', 'name', 'pin', 'date_created']


admin.site.register(Grow, admin.OSMGeoAdmin)
admin.site.register(Rack, admin.OSMGeoAdmin)
admin.site.register(Tray, admin.OSMGeoAdmin)
admin.site.register(TrayPosition, admin.OSMGeoAdmin)
admin.site.register(Sensor)
admin.site.register(GrowSensorPreferences)
admin.site.register(SensorSetupToken, SensorSetupTokenAdmin)
admin.site.register(SensorUpdate)
admin.site.register(SensorAuthenticationToken, SensorAuthenticationTokenAdmin)
admin.site.register(SensorRelay, SensorRelayAdmin)
admin.site.register(RelaySchedule, RelayScheduleAdmin)
admin.site.register(SensorSwitch, SensorSwitchAdmin)

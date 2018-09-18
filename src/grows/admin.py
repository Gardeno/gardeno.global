from django.contrib.gis import admin
from .models import Grow, Rack, Tray, TrayPosition, Sensor, AWSGreengrassCore, AWSGreengrassGroup, \
    GrowSensorPreferences, SensorSetupToken, SensorUpdate, SensorAuthenticationToken


class SensorSetupTokenAdmin(admin.ModelAdmin):
    readonly_fields = ['date_created']
    list_display = ['date_created', 'identifier', 'sensor', 'date_last_downloaded']


class SensorAuthenticationTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'date_created', 'date_deactivated', 'sensor', 'date_last_used']


admin.site.register(Grow, admin.OSMGeoAdmin)
admin.site.register(Rack, admin.OSMGeoAdmin)
admin.site.register(Tray, admin.OSMGeoAdmin)
admin.site.register(TrayPosition, admin.OSMGeoAdmin)
admin.site.register(Sensor)
admin.site.register(AWSGreengrassCore)
admin.site.register(AWSGreengrassGroup)
admin.site.register(GrowSensorPreferences)
admin.site.register(SensorSetupToken, SensorSetupTokenAdmin)
admin.site.register(SensorUpdate)
admin.site.register(SensorAuthenticationToken, SensorAuthenticationTokenAdmin)

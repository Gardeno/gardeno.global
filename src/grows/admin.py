from django.contrib.gis import admin
from .models import Grow, Rack, Tray, TrayPosition, Sensor, AWSGreengrassCore, AWSGreengrassGroup, \
    GrowSensorPreferences, AWSGreengrassCoreSetupToken


class AWSGreengrassCoreSetupTokenAdmin(admin.ModelAdmin):
    readonly_fields = ['date_created']
    list_display = ['date_created', 'identifier', 'aws_greengrass_core', 'date_last_downloaded']


admin.site.register(Grow, admin.OSMGeoAdmin)
admin.site.register(Rack, admin.OSMGeoAdmin)
admin.site.register(Tray, admin.OSMGeoAdmin)
admin.site.register(TrayPosition, admin.OSMGeoAdmin)
admin.site.register(Sensor)
admin.site.register(AWSGreengrassCore)
admin.site.register(AWSGreengrassGroup)
admin.site.register(GrowSensorPreferences)
admin.site.register(AWSGreengrassCoreSetupToken, AWSGreengrassCoreSetupTokenAdmin)

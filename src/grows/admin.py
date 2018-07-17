from django.contrib.gis import admin
from .models import Grow, Rack, Tray, TrayPosition, Sensor, AWSGreengrassCore, AWSGreengrassGroup, GrowSensorPreferences

admin.site.register(Grow, admin.OSMGeoAdmin)
admin.site.register(Rack, admin.OSMGeoAdmin)
admin.site.register(Tray, admin.OSMGeoAdmin)
admin.site.register(TrayPosition, admin.OSMGeoAdmin)
admin.site.register(Sensor)
admin.site.register(AWSGreengrassCore)
admin.site.register(AWSGreengrassGroup)
admin.site.register(GrowSensorPreferences)

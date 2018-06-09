from django.contrib.gis import admin
from .models import HazardIdentification, NearMiss, Incident

admin.site.register(HazardIdentification, admin.OSMGeoAdmin)
admin.site.register(NearMiss, admin.OSMGeoAdmin)
admin.site.register(Incident, admin.OSMGeoAdmin)

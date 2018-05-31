from django.contrib.gis import admin
from .models import Grow, Rack

admin.site.register(Grow, admin.OSMGeoAdmin)
admin.site.register(Rack, admin.OSMGeoAdmin)

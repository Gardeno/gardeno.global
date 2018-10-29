from django.contrib import admin
from salads.models import *


class SaladInline(admin.TabularInline):
    model = Salad
    extra = 0


admin.site.register(Microgreen)
admin.site.register(Ingredient)
admin.site.register(Dressing)
admin.site.register(SaladTemplate)
admin.site.register(Salad)

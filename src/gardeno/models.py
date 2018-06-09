from django.contrib.gis.db import models


class BaseModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_archived = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

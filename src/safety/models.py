from django.db import models
from django.contrib.gis.db import models
from gardeno.models import BaseModel
from accounts.models import User


class BaseSafetyModel(BaseModel):
    location = models.PointField(null=True)
    description = models.TextField(null=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class HazardIdentification(BaseSafetyModel):
    pass


class NearMiss(BaseSafetyModel):
    pass


class Incident(BaseSafetyModel):
    pass

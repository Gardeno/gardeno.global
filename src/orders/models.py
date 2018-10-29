from django.db import models
from hashids import Hashids
from django.conf import settings
from timezone_field import TimeZoneField
from accounts.models import Customer

hashids = Hashids(salt='{}_orders'.format(settings.HASH_IDS_BASE_SALT), min_length=8)


class Order(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(Customer, null=True, on_delete=models.CASCADE)
    timezone = TimeZoneField(null=True)

    @property
    def hashed_id(self):
        return hashids.encode(self.id)

    @property
    def label_url(self):
        return "/orders/{}/label/".format(self.id)

    @staticmethod
    def get_by_hashed_id(hash_id):
        try:
            return Order.objects.get(id=hashids.decode(hash_id)[0])
        except:
            return None

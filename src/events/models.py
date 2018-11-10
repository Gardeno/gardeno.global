from django.db import models
from hashids import Hashids
from django.conf import settings
from timezone_field import TimeZoneField

hashids = Hashids(salt='{}_events'.format(settings.HASH_IDS_BASE_SALT), min_length=8)


class Event(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, null=True)
    event_start_utc = models.DateTimeField(null=True, verbose_name='Event start')
    event_end_utc = models.DateTimeField(null=True, verbose_name='Event end')
    timezone = TimeZoneField(null=True)

    def __str__(self):
        return self.name

    @property
    def hashed_id(self):
        return hashids.encode(self.id)

    @property
    def label_url(self):
        return "/events/{}/label/".format(self.id)

    @property
    def salad_url(self):
        return "/events/{}/salads/".format(self.hashed_id)

    @staticmethod
    def get_by_hashed_id(hash_id):
        try:
            return Event.objects.get(id=hashids.decode(hash_id)[0])
        except:
            return None

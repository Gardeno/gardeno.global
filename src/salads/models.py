from django.db import models
from grows.models import Grow
from hashids import Hashids
from django.conf import settings


class NamedField(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Microgreen(NamedField):
    grow = models.ForeignKey(Grow, null=True, blank=True, on_delete=models.SET_NULL)


class Ingredient(NamedField):
    pass


class Dressing(NamedField):
    pass


class SaladTemplate(NamedField):
    grow = models.ForeignKey(Grow, null=True, blank=True, on_delete=models.SET_NULL)
    microgreens = models.ManyToManyField(Microgreen)
    ingredients = models.ManyToManyField(Ingredient)
    dressings = models.ManyToManyField(Dressing, blank=True)


class Salad(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    grow = models.ForeignKey(Grow, null=True, blank=True, on_delete=models.SET_NULL)
    from_template = models.ForeignKey(SaladTemplate, null=True, blank=True, on_delete=models.SET_NULL)
    # Additional ingredients
    added_microgreens = models.ManyToManyField(Microgreen, blank=True, related_name='added_microgreens')
    added_ingredients = models.ManyToManyField(Ingredient, blank=True, related_name='added_ingredients')
    added_dressings = models.ManyToManyField(Dressing, blank=True, related_name='added_dressings')
    # Removed ingredients
    removed_microgreens = models.ManyToManyField(Microgreen, blank=True, related_name='removed_microgreens')
    removed_ingredients = models.ManyToManyField(Ingredient, blank=True, related_name='removed_ingredients')
    removed_dressings = models.ManyToManyField(Dressing, blank=True, related_name='removed_dressings')

    @property
    def hashed_id(self):
        hashids = Hashids(salt='{}_{}'.format(settings.HASH_IDS_BASE_SALT,
                                              self.grow.identifier), min_length=8)
        return hashids.encode(self.id)

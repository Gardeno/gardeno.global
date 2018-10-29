from django.db import models
from grows.models import Grow
from hashids import Hashids
from django.conf import settings
from orders.models import Order
from events.models import Event

hashids = Hashids(salt='salads_{}'.format(settings.HASH_IDS_BASE_SALT), min_length=8)


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

    # For now, a salad is either part of an order or
    # part of an event.

    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL, related_name='salads')
    event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.SET_NULL, related_name='salads')

    @property
    def hashed_id(self):
        return hashids.encode(self.id)

    @staticmethod
    def get_by_hashed_id(hash_id):
        try:
            return Salad.objects.get(id=hashids.decode(hash_id)[0])
        except:
            return None

    @property
    def generate_link(self):
        base_url = 'https://gardeno.global'
        if self.order:
            base_url += '/orders/{}'.format(self.order.hashed_id)
        elif self.event:
            base_url += '/events/{}'.format(self.event.hashed_id)
        else:
            return base_url
        base_url += '/salads/{}/'.format(self.hashed_id)
        return base_url

    @property
    def generate_ingredients_string(self):
        ingredient_parts = []
        if self.from_template:
            if self.from_template.microgreens.count() > 0:
                ingredient_parts.append('Microgreens')
            for ingredient in self.from_template.ingredients.all():
                ingredient_parts.append('{}'.format(ingredient))
        return ', '.join(ingredient_parts)


class SaladFeedback(models.Model):
    salad = models.ForeignKey(Salad, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

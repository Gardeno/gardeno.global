from django.forms import models
from .models import Grow, Sensor
from django.forms.widgets import TextInput, CheckboxInput, Select


class GrowForm(models.ModelForm):
    class Meta:
        model = Grow
        fields = [
            'title',
            'is_live',
        ]
        widgets = {
            "title": TextInput(attrs={
                "placeholder": "Enter grow title...",
            }),
            "is_live": CheckboxInput(),
        }


class GrowSensorForm(models.ModelForm):
    class Meta:
        model = Sensor
        fields = ['type']
        widgets = {
            "type": Select(attrs={
                "required": True
            }),
        }

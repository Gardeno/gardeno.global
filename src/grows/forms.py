from django.forms import models
from .models import Grow
from django.forms.widgets import TextInput, CheckboxInput


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

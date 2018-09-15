from django.forms import models, ValidationError
from .models import Grow, Sensor, GrowSensorPreferences
from django.forms.widgets import TextInput, CheckboxInput, Select
from django_countries.widgets import CountrySelectWidget
from sshpubkeys import SSHKey, InvalidKeyError


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
        fields = ['name', 'type']
        widgets = {
            "name": TextInput(attrs={
                "required": True,
                "placeholder": "Enter a memorable name for this sensor"
            }),
            "type": Select(attrs={
                "required": True
            }),
        }


class GrowSensorPreferencesForm(models.ModelForm):
    class Meta:
        model = GrowSensorPreferences
        fields = ['wifi_network_name', 'wifi_password', 'wifi_type', 'wifi_country_code',
                  'publish_ssh_key_for_authentication', 'sensor_user_password']
        widgets = {'country': CountrySelectWidget()}

    def clean_publish_ssh_key_for_authentication(self):
        public_key = self.cleaned_data['publish_ssh_key_for_authentication']
        if public_key:
            ssh_key = SSHKey(public_key)
            try:
                ssh_key.parse()
            except InvalidKeyError as err:
                raise ValidationError("Invalid key: {}".format(err))
            except NotImplementedError as err:
                raise ValidationError("Invalid key type: {}".format(err))
        return public_key

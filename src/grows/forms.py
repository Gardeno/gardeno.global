from django import forms
from .models import Grow, Sensor, GrowSensorPreferences, SensorRelay, SensorSwitch, SwitchTrigger
from django.forms.widgets import TextInput, CheckboxInput, Select, TimeInput
from django_countries.widgets import CountrySelectWidget
from sshpubkeys import SSHKey, InvalidKeyError
import pytz
from datetime import datetime


class TimeZoneFormField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):

        def coerce_to_pytz(val):
            try:
                return pytz.timezone(val)
            except pytz.UnknownTimeZoneError:
                raise forms.ValidationError("Unknown time zone: '%s'" % val)

        def build_timezones():
            yield (None, '---Choose the grow\'s timezone---')
            for common_timezone in pytz.common_timezones:
                offset = datetime.now(pytz.timezone(common_timezone)).strftime('%z')
                yield (common_timezone, '{} (GMT{})'.format(common_timezone.replace('_', ' '),
                                                            offset))

        defaults = {
            'coerce': coerce_to_pytz,
            'choices': build_timezones(),
            'empty_value': None,
        }
        defaults.update(kwargs)
        super(TimeZoneFormField, self).__init__(*args, **defaults)


class GrowForm(forms.models.ModelForm):
    timezone = TimeZoneFormField()

    class Meta:
        model = Grow
        fields = [
            'title',
            'timezone',
            'is_live',
        ]
        widgets = {
            "title": TextInput(attrs={
                "placeholder": "Enter grow title...",
            }),
            "is_live": CheckboxInput(),
        }


class GrowSensorForm(forms.models.ModelForm):
    class Meta:
        model = Sensor
        fields = ['name', ]
        widgets = {
            "name": TextInput(attrs={
                "required": True,
                "placeholder": "Enter a memorable name for this sensor"
            }),
        }


class GrowSensorRelayForm(forms.models.ModelForm):
    class Meta:
        model = SensorRelay
        fields = ['name', 'pin']
        widgets = {
            "name": TextInput(attrs={
                "required": True,
                "placeholder": "Enter a memorable name for this relay"
            }),
            "pin": TextInput(attrs={
                "type": "number",
                "placeholder": "Enter the GPIO pin this relay is connected to",
                "required": True
            }),
        }


class GrowSensorRelayScheduleForm(forms.Form):
    execution_time = forms.TimeField(
        widget=TimeInput(attrs={'placeholder': 'Enter the time when this action will run'}))
    action = forms.ChoiceField(choices=(('On', 'Turn On'), ('Off', 'Turn Off')))
    is_enabled = forms.BooleanField()


class GrowSensorPreferencesForm(forms.models.ModelForm):
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
                raise forms.ValidationError("Invalid key: {}".format(err))
            except NotImplementedError as err:
                raise forms.ValidationError("Invalid key type: {}".format(err))
        return public_key


class GrowSensorSwitchForm(forms.models.ModelForm):
    class Meta:
        model = SensorSwitch
        fields = ['name', 'pin']
        widgets = {
            "name": TextInput(attrs={
                "required": True,
                "placeholder": "Enter a memorable name for this switch"
            }),
            "pin": TextInput(attrs={
                "type": "number",
                "placeholder": "Enter the GPIO pin this switch is connected to",
                "required": True
            }),
        }


class GrowSensorSwitchTriggerForm(forms.models.ModelForm):
    def __init__(self, *args, **kwargs):
        grow = kwargs.pop('grow')
        super(GrowSensorSwitchTriggerForm, self).__init__(*args, **kwargs)
        self.fields['trigger_relay'].queryset = SensorRelay.objects.filter(sensor__grow=grow)

    class Meta:
        model = SwitchTrigger
        fields = ['triggered_when_switch_is', 'after_sustained_for_seconds', 'trigger_relay']

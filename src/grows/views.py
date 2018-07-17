from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import GrowForm, GrowSensorForm, GrowSensorPreferencesForm
from .models import Grow, Sensor, GrowSensorPreferences, AWSGreengrassCoreSetupToken, VISIBILITY_OPTION_VALUES, \
    SENSOR_TYPES, SENSOR_AWS_TYPE_LOOKUP
import uuid
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, Http404
from .decorators import lookup_grow, must_own_grow, lookup_sensor, must_have_created_core
from datetime import datetime, timezone
from django.conf import settings
import os
import secrets
import string

alphabet = string.ascii_letters + string.digits


def grows_list(request):
    is_mine = request.user.is_authenticated
    if 'type' in request.GET:
        requested_type = request.GET.get('type', 'community')
        if requested_type in ['mine', 'community']:
            if requested_type == 'mine':
                if not request.user.is_authenticated:
                    return HttpResponseRedirect('/accounts/login/?next=/grows/create/')
                is_mine = True
            else:
                is_mine = False
    if is_mine:
        grows = Grow.objects.filter(created_by_user=request.user)
    else:
        grows = Grow.objects.filter(date_published__isnull=False, visibility='Public')
    return render(request, 'grows/list.html', {
        "is_mine": is_mine,
        "grows": grows,
    })


@login_required
def grows_create(request):
    error = None
    form = GrowForm()
    if request.POST:
        form = GrowForm(request.POST)
        if form.is_valid():
            if request.user.created_grows.filter(date_archived__isnull=True).count() >= request.user.grow_limit:
                return HttpResponseRedirect("/grows/exceeded/")
            grow = Grow.objects.create(identifier=uuid.uuid4(),
                                       title=form.data['title'],
                                       is_live=form.data['is_live'] == 'on',
                                       created_by_user=request.user)
            grow.create_greengrass_group()
            return HttpResponseRedirect("/grows/{}/".format(grow.identifier))
        else:
            error = 'Form is invalid'
    return render(request, 'grows/create.html', {
        "form": form,
        "error": error,
    })


@login_required
def grows_exceeded(request):
    return render(request, 'grows/exceeded.html', {})


@lookup_grow
def grows_detail(request):
    template = 'grows/detail/edit/dashboard.html' if request.grow.is_owned_by_user(
        request.user) else 'grows/detail/view/dashboard.html'
    return render(request, template, {
        "grow": request.grow,
    })


@lookup_grow
@must_own_grow
def grows_detail_group(request):
    if request.grow.has_created_greengrass_group:
        return HttpResponseRedirect('/grows/{}/'.format(request.grow.identifier))
    error = None
    if request.POST:
        success = request.grow.create_greengrass_group()
        if success:
            return HttpResponseRedirect('/grows/{}/'.format(request.grow.identifier))
        else:
            error = "Unable to create group at this time. Please try again later."
    return render(request, 'grows/detail/edit/group.html', {
        "grow": request.grow,
        "error": error
    })


@lookup_grow
@must_own_grow
def grows_detail_sensors(request):
    template = 'grows/detail/edit/sensors/index.html' if request.grow.is_owned_by_user(
        request.user) else 'grows/detail/view/sensors/index.html'
    return render(request, template, {
        "grow": request.grow,
        "active_view": "sensors",
        "available_sensor_types": SENSOR_TYPES
    })


@lookup_grow
@must_own_grow
def grows_detail_sensors_preferences(request):
    error = None
    existing_preferences, _ = GrowSensorPreferences.objects.get_or_create(grow=request.grow)
    form = GrowSensorPreferencesForm(instance=existing_preferences)
    if request.POST:
        form = GrowSensorPreferencesForm(request.POST, instance=existing_preferences)
        if form.is_valid():
            grow_sensor_preferences_instance = form.save(commit=False)
            grow_sensor_preferences_instance.grow = request.grow
            grow_sensor_preferences_instance.save()
            return HttpResponseRedirect("/grows/{}/sensors/".format(request.grow.identifier))
        else:
            print(form.errors)
            error = 'Form is invalid'
    return render(request, 'grows/detail/edit/sensors/preferences.html', {
        "grow": request.grow,
        "active_view": "sensors",
        "form": form,
        "error": error,
    })


@lookup_grow
@must_own_grow
def grows_detail_sensors_core(request):
    grow_url = '/grows/{}/sensors/'.format(request.grow.identifier)
    if not request.POST or request.grow.has_created_greengrass_core:
        return HttpResponseRedirect(grow_url)
    if not request.grow.create_greengrass_core():
        return HttpResponseRedirect('{}?error'.format(grow_url))
    else:
        return HttpResponseRedirect(grow_url)


@lookup_grow
@must_own_grow
def grows_detail_sensors_core_recipe(request):
    if not hasattr(request.grow, 'aws_greengrass_core'):
        return HttpResponseBadRequest('Need to create a core before generating the recipe.')
    aws_greengrass_core = request.grow.aws_greengrass_core
    setup_token = AWSGreengrassCoreSetupToken.objects.create(aws_greengrass_core=aws_greengrass_core,
                                                             identifier=uuid.uuid4())
    with open(os.path.join(settings.STATIC_ROOT, 'grow_templates', 'WithWifi.xml')) as xml_file:
        read_xml_file = ''.join(xml_file.readlines())
        read_xml_file = read_xml_file.replace('SENSOR_HOSTNAME',
                                              'core-{}'.format(aws_greengrass_core.core_id))
        read_xml_file = read_xml_file.replace('DOWNLOAD_FILE_URL',
                                              '{}/grows/{}/sensors/core/setup/{}/'.format(settings.SITE_URL,
                                                                                          request.grow.identifier,
                                                                                          setup_token.identifier))
        generated_user_password = None
        if hasattr(request.grow, 'preferences'):
            read_xml_file = read_xml_file.replace('NETWORK_NAME', request.grow.preferences.wifi_network_name)
            read_xml_file = read_xml_file.replace('NETWORK_PASSWORD', request.grow.preferences.wifi_password)
            read_xml_file = read_xml_file.replace('NETWORK_TYPE', request.grow.preferences.wifi_type)
            read_xml_file = read_xml_file.replace('NETWORK_ISO_3166_COUNTRY',
                                                  request.grow.preferences.wifi_country_code.code)
            read_xml_file = read_xml_file.replace('PUBLIC_SSH_KEY',
                                                  request.grow.preferences.publish_ssh_key_for_authentication)
            if request.grow.preferences.sensor_user_password:
                generated_user_password = request.grow.preferences.sensor_user_password
        if not generated_user_password:
            generated_user_password = ''.join(
                secrets.choice(alphabet) for _ in range(10))  # for a 20-character password
        read_xml_file = read_xml_file.replace('USER_PASSWORD', generated_user_password)
        response = HttpResponse(read_xml_file, content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename={}-core.xml'.format(request.grow)
        return response


def grows_detail_sensors_core_setup(request, grow_id=None, setup_id=None):
    # No authentication decorators because the setup_id is an expiring token
    try:
        grow = Grow.objects.get(identifier=grow_id)
    except:
        raise Http404
    try:
        setup_token = AWSGreengrassCoreSetupToken.objects.get(aws_greengrass_core__grow=grow,
                                                              identifier=setup_id)
    except:
        raise Http404
    if (datetime.now(timezone.utc) - setup_token.date_created).total_seconds() > 60 * 60 * 24:
        return HttpResponseBadRequest('Setup script has expired')
    with open(os.path.join(settings.STATIC_ROOT, 'grow_templates', 'setup_greengrass.sh')) as executable_file:
        read_executable_file = ''.join(executable_file.readlines())
        response = HttpResponse(read_executable_file, content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename={}-greengrass_setup.sh'.format(grow)
        setup_token.date_last_downloaded = datetime.now(timezone.utc)
        setup_token.save()
        return response


@lookup_grow
@must_own_grow
@must_have_created_core
def grows_detail_sensors_create(request):
    initial_type = request.GET.get('type', 'Ambient')
    error = None
    form = GrowSensorForm(initial={
        'type': initial_type,
    })
    if request.POST:
        form = GrowSensorForm(request.POST)
        if form.is_valid():
            sensor_type = form.data['type']
            sensor = Sensor.objects.create(grow=request.grow,
                                           identifier=uuid.uuid4(),
                                           created_by_user=request.user,
                                           type=sensor_type)
            response = settings.IOT_CLIENT.create_thing(
                thingName='{}__{}'.format(request.grow.identifier, sensor.identifier),
                thingTypeName=SENSOR_AWS_TYPE_LOOKUP[sensor_type],
                attributePayload={
                    'attributes': {
                        'grow_id': '{}'.format(request.grow.identifier),
                        'sensor_id': '{}'.format(sensor.identifier),
                    }
                }
            )
            sensor.aws_thing_name = response['thingName']
            sensor.aws_thing_arn = response['thingArn']
            sensor.aws_thing_id = response['thingId']
            sensor.save()
            return HttpResponseRedirect("/grows/{}/sensors/{}/".format(request.grow.identifier, sensor.identifier))
        else:
            error = 'Form is invalid'
    return render(request, 'grows/detail/edit/sensors/create.html', {
        "grow": request.grow,
        "form": form,
        "error": error,
        "active_view": "sensors",
        "available_sensor_types": SENSOR_TYPES,
        "initial_type": initial_type,
    })


@lookup_grow
@must_own_grow
@lookup_sensor
@must_have_created_core
def grows_detail_sensors_detail(request):
    template = 'grows/detail/edit/sensors/detail.html' if request.grow.is_owned_by_user(
        request.user) else 'grows/detail/view/sensors/detail.html'
    return render(request, template, {
        "grow": request.grow,
        "sensor": request.sensor,
        "active_view": "sensors",
    })


@lookup_grow
def grows_detail_update(request):
    if not request.POST:
        return HttpResponseRedirect('/grows/{}'.format(request.grow.identifier))
    visibility = request.POST.get('visibility', None)
    if visibility not in VISIBILITY_OPTION_VALUES:
        return HttpResponseBadRequest('Visibility must be one of {}'.format(', '.join(VISIBILITY_OPTION_VALUES)))
    request.grow.visibility = visibility
    if 'publish' in request.POST:
        if request.grow.date_published:
            return HttpResponseBadRequest('Grow has already been published!')
        else:
            request.grow.date_published = datetime.utcnow()
            request.grow.save()
    elif 'save' in request.POST:
        request.grow.save()
    else:
        return HttpResponseBadRequest('Can only publish or save')
    return HttpResponseRedirect('/grows/{}'.format(request.grow.identifier))

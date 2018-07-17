from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import GrowForm, GrowSensorForm
from .models import Grow, Sensor, VISIBILITY_OPTION_VALUES, SENSOR_TYPES, SENSOR_AWS_TYPE_LOOKUP
import uuid
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest
from .decorators import lookup_grow, must_own_grow, lookup_sensor, must_have_created_core
from datetime import datetime
from django.conf import settings


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

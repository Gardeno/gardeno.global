from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import GrowForm
from .models import Grow, VISIBILITY_OPTION_VALUES
import uuid
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest
from .decorators import lookup_grow
from datetime import datetime


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
            grow = Grow.objects.create(identifier=uuid.uuid4(),
                                       title=form.data['title'],
                                       is_live=form.data['is_live'] == 'on',
                                       created_by_user=request.user)
            return HttpResponseRedirect("/grows/{}/".format(grow.identifier))
        else:
            error = 'Form is invalid'
    return render(request, 'grows/create.html', {
        "form": form,
        "error": error,
    })


@lookup_grow
def grows_detail(request):
    template = 'grows/detail/edit/dashboard.html' if request.grow.is_owned_by_user(
        request.user) else 'grows/detail/view/dashboard.html'
    return render(request, template, {
        "grow": request.grow,
    })


@lookup_grow
def grows_detail_sensors(request):
    template = 'grows/detail/edit/sensors/index.html' if request.grow.is_owned_by_user(
        request.user) else 'grows/detail/view/sensors/index.html'
    return render(request, template, {
        "grow": request.grow,
        "active_view": "sensors",
    })


@lookup_grow
def grows_detail_update(request):
    if not request.POST:
        return HttpResponseRedirect('../')
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
    return HttpResponseRedirect('../')

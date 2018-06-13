from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import GrowForm
from .models import Grow
import uuid
from django.http import HttpResponseRedirect, Http404


def grows_list(request):
    return render(request, 'grows/list.html')


@login_required
def grows_create(request):
    error = None
    form = GrowForm()
    if request.POST:
        form = GrowForm(request.POST)
        if form.is_valid():
            grow = Grow.objects.create(identifier=uuid.uuid4(),
                                       title=form.data['title'],
                                       is_live=form.data['is_live'] == 'on')
            return HttpResponseRedirect("/grows/{}/".format(grow.identifier))
        else:
            error = 'Form is invalid'
    return render(request, 'grows/create.html', {
        "form": form,
        "error": error,
    })


def grows_detail(request, grow_id=None):
    try:
        grow = Grow.objects.get(identifier=grow_id)
    except Exception as exception:
        raise Http404
    owned_by_user = grow.created_by_user and request.user.id == grow.created_by_user.id
    if not owned_by_user:
        if not grow.date_published or grow.visibility == 'Private':
            raise Http404
        else:
            return render(request, 'grows/detail/view.html', {
                "grow": grow,
            })
    else:
        return render(request, 'grows/detail/edit.html', {
            "grow": grow,
        })

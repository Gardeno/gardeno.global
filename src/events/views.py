from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseRedirect
from events.models import Event
from salads.models import Salad, SaladFeedback
import csv


@login_required
def events_detail_label(request, event_id):
    try:
        # TODO: Ensure only user can generate this label
        event = Event.objects.get(id=event_id)
    except:
        raise Http404
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="event-{}.csv"'.format(event_id)
    writer = csv.writer(response)
    writer.writerow(['Salad Name', 'Salad Link', 'Salad Ingredients'])
    for salad in event.salads.all():
        writer.writerow([salad.from_template.name, salad.generate_link, salad.generate_ingredients_string])
    return response


def events_detail_salad_lookup(request, event_hash_id, salad_hash_id):
    event = Event.get_by_hashed_id(event_hash_id)
    salad = Salad.get_by_hashed_id(salad_hash_id)
    if not event or not salad:
        return HttpResponseRedirect('/')
    if request.POST:
        SaladFeedback.objects.create(salad=salad, email=request.POST.get('email', None),
                                     comments=request.POST.get('comments', None))

    return render(request, 'events/salad.html', {
        "event": event,
        "salad": salad,
    })

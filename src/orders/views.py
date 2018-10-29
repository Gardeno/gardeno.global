from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseRedirect
from orders.models import Order
from salads.models import Salad
import csv


@login_required
def orders_detail_label(request, order_id):
    try:
        # TODO: Ensure only user can generate this label
        order = Order.objects.get(id=order_id)
    except:
        raise Http404
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="order-{}.csv"'.format(order_id)
    writer = csv.writer(response)
    writer.writerow(['Salad Name', 'Salad Link', 'Salad Ingredients'])
    for salad in order.salads.all():
        writer.writerow([salad.from_template.name, salad.generate_link, salad.generate_ingredients_string])
    return response


def orders_detail_salad_lookup(request, order_hash_id, salad_hash_id):
    order = Order.get_by_hashed_id(order_hash_id)
    salad = Salad.get_by_hashed_id(salad_hash_id)
    if not order or not salad:
        return HttpResponseRedirect('/')
    return HttpResponse('Thanks')

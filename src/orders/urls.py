from django.urls import path
from .views import orders_detail_label, orders_detail_salad_lookup

urlpatterns = [
    path('<order_id>/label/', orders_detail_label),
    path('<order_hash_id>/salads/<salad_hash_id>/', orders_detail_salad_lookup),
]

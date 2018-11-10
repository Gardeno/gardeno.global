from django.urls import path
from .views import events_detail_label, events_detail_salad_lookup

urlpatterns = [
    path('<event_id>/label/', events_detail_label),
    path('<event_hash_id>/salads/', events_detail_salad_lookup),
    path('<event_hash_id>/salads/<salad_hash_id>/', events_detail_salad_lookup),
]

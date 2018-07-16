from django.urls import path
from .views import grows_list, grows_create, grows_detail, grows_detail_sensors, grows_detail_update

urlpatterns = [
    path('', grows_list),
    path('create/', grows_create),
    path('<grow_id>/', grows_detail),
    path('<grow_id>/sensors/', grows_detail_sensors),
    path('<grow_id>/update/', grows_detail_update),
]

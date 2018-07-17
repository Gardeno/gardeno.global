from django.urls import path
from .views import grows_list, grows_create, grows_detail, grows_detail_sensors, grows_detail_sensors_create, \
    grows_detail_update, grows_detail_sensors_detail, grows_exceeded, grows_detail_group, grows_detail_sensors_core, \
    grows_detail_sensors_preferences

urlpatterns = [
    path('', grows_list),
    path('create/', grows_create),
    path('exceeded/', grows_exceeded),
    path('<grow_id>/', grows_detail),
    path('<grow_id>/group/', grows_detail_group),
    path('<grow_id>/sensors/', grows_detail_sensors),
    path('<grow_id>/sensors/preferences/', grows_detail_sensors_preferences),
    path('<grow_id>/sensors/core/', grows_detail_sensors_core),
    path('<grow_id>/sensors/create/', grows_detail_sensors_create),
    path('<grow_id>/sensors/<sensor_id>/', grows_detail_sensors_detail),
    path('<grow_id>/update/', grows_detail_update),
]

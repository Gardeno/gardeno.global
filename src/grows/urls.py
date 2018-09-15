from django.urls import path
from .views import grows_list, grows_create, grows_detail, grows_detail_sensors, grows_detail_sensors_create, \
    grows_detail_update, grows_detail_sensors_detail, grows_exceeded, grows_detail_group, \
    grows_detail_sensors_preferences, grows_detail_sensors_detail_recipe, grows_detail_sensors_detail_setup, \
    grows_detail_sensors_detail_setup_finished

urlpatterns = [
    path('', grows_list),
    path('create/', grows_create),
    path('exceeded/', grows_exceeded),
    path('<grow_id>/', grows_detail),
    path('<grow_id>/group/', grows_detail_group),
    path('<grow_id>/sensors/', grows_detail_sensors),
    path('<grow_id>/sensors/preferences/', grows_detail_sensors_preferences),
    path('<grow_id>/sensors/create/', grows_detail_sensors_create),
    path('<grow_id>/sensors/<sensor_id>/', grows_detail_sensors_detail),
    path('<grow_id>/sensors/<sensor_id>/recipe/', grows_detail_sensors_detail_recipe),
    path('<grow_id>/sensors/<sensor_id>/setup/<setup_id>/', grows_detail_sensors_detail_setup),
    path('<grow_id>/sensors/<sensor_id>/setup/<setup_id>/finished/', grows_detail_sensors_detail_setup_finished),
    path('<grow_id>/update/', grows_detail_update),
]

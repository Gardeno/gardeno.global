from django.urls import path
from .views import grows_list, grows_create, grows_detail, grows_detail_sensors, grows_detail_sensors_create, \
    grows_detail_update, grows_detail_sensors_detail, grows_exceeded, \
    grows_detail_sensors_preferences, grows_detail_sensors_detail_recipe, grows_detail_sensors_detail_setup, \
    grows_detail_sensors_detail_setup_finished, grows_detail_sensors_detail_update, \
    grows_detail_sensors_detail_executable, grows_detail_sensors_detail_requirements, \
    grows_detail_sensors_detail_environment, grows_detail_sensors_detail_vpn_config, \
    grows_detail_sensors_detail_relay_create, grows_detail_sensors_detail_relay_detail

urlpatterns = [
    path('', grows_list),
    path('create/', grows_create),
    path('exceeded/', grows_exceeded),
    path('<grow_id>/', grows_detail),
    path('<grow_id>/sensors/', grows_detail_sensors),
    path('<grow_id>/sensors/preferences/', grows_detail_sensors_preferences),
    path('<grow_id>/sensors/create/', grows_detail_sensors_create),
    path('<grow_id>/sensors/<sensor_id>/', grows_detail_sensors_detail),
    path('<grow_id>/sensors/<sensor_id>/recipe/', grows_detail_sensors_detail_recipe),
    path('<grow_id>/sensors/<sensor_id>/setup/<setup_id>/', grows_detail_sensors_detail_setup),
    path('<grow_id>/sensors/<sensor_id>/setup/<setup_id>/finished/', grows_detail_sensors_detail_setup_finished),
    path('<grow_id>/sensors/<sensor_id>/update/', grows_detail_sensors_detail_update),
    path('<grow_id>/sensors/<sensor_id>/executable/', grows_detail_sensors_detail_executable),
    path('<grow_id>/sensors/<sensor_id>/requirements/', grows_detail_sensors_detail_requirements),
    path('<grow_id>/sensors/<sensor_id>/environment/', grows_detail_sensors_detail_environment),
    path('<grow_id>/sensors/<sensor_id>/vpn_config/', grows_detail_sensors_detail_vpn_config),
    path('<grow_id>/sensors/<sensor_id>/relays/create/', grows_detail_sensors_detail_relay_create),
    path('<grow_id>/sensors/<sensor_id>/relays/<relay_id>/', grows_detail_sensors_detail_relay_detail),
    path('<grow_id>/update/', grows_detail_update),
]

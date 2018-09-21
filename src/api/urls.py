from django.urls import path
from .views import accounts_sign_in, accounts_sign_up, accounts_me, accounts_my_grows, grow_sensor_relay_action

urlpatterns = [
    path('accounts/signin/', accounts_sign_in),
    path('accounts/signup/', accounts_sign_up),
    path('accounts/me/', accounts_me),
    path('accounts/me/grows/', accounts_my_grows),
    path('grows/<grow_id>/sensors/<sensor_id>/relays/<relay_id>/action/<action_type>/', grow_sensor_relay_action),
]

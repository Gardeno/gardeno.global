from django.urls import path
from .views import accounts_sign_in, accounts_sign_up, accounts_me, accounts_my_grows

urlpatterns = [
    path('accounts/signin/', accounts_sign_in),
    path('accounts/signup/', accounts_sign_up),
    path('accounts/me/', accounts_me),
    path('accounts/me/grows/', accounts_my_grows),
]

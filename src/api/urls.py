from django.urls import path
from .views import accounts_sign_in, accounts_sign_up

urlpatterns = [
    path('accounts/signin/', accounts_sign_in),
    path('accounts/signup/', accounts_sign_up),
]

from django.urls import path
from .views import accounts_sign_up

urlpatterns = [
    path('accounts/signup/', accounts_sign_up),
]

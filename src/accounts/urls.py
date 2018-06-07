from django.urls import path
from .views import accounts_login

urlpatterns = [
    path('login/', accounts_login),
]

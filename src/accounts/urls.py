from django.urls import path
from .views import accounts_login, accounts_signup, accounts_logout

urlpatterns = [
    path('login/', accounts_login),
    path('signup/', accounts_signup),
    path('logout/', accounts_logout),
]

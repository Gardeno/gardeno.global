from django.urls import path
from .views import grows_list, grows_create

urlpatterns = [
    path('', grows_list),
    path('create/', grows_create),
]

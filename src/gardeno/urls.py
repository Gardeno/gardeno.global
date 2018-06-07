from django.contrib import admin
from django.urls import include, path
from .views import index, notify

urlpatterns = [
    path('', index),
    path('notify', notify),
    path('grows/', include('grows.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
]
from django.contrib import admin
from django.urls import include, path
from .views import index, notify

urlpatterns = [
    path('', index),
    path('notify', notify),
    path('grows/', include('grows.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    path('events/', include('events.urls')),
    path('admin/queues/', include('django_rq.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
]

from django.urls import path
from .views import index, url_spoof

urlpatterns = [
    path('', index, name='index'),
    path('url_spoof', url_spoof, name='url_spoof'),
]
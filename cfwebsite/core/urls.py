from django.urls import path
from .views import index, url_spoof, mouse, mouse_log
from django.views.static import serve
from django.conf import settings


urlpatterns = [
    path(
        'scripts/<path:path>',
        serve,
        {'document_root': settings.BASE_DIR / 'core' / 'templates' / 'scripts'}
    ),
    path('', index, name='index'),
    path('url_spoof', url_spoof, name='url_spoof'),
    path('mouse', mouse, name='mouse'),
    path("mouse-log/", mouse_log, name="mouse-log"),


]
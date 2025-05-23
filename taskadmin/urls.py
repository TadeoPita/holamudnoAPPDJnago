# taskadmin/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from proyecto.views import inicio
from tarea import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('proyectos/', include('proyecto.urls')),
    path('', inicio, name='inicio'),
    path('tarea/', include('tarea.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from . import views

urlpatterns = [
    path('mi-calendario/', views.mi_calendario, name='mi_calendario'),
    path('eventos/crear/', views.crear_evento_personal, name='crear_evento_personal'),
    path('eventos/<int:evento_id>/actualizar/', views.actualizar_evento_personal, name='actualizar_evento_personal'),
    path('eventos/<int:evento_id>/eliminar/', views.eliminar_evento_personal, name='eliminar_evento_personal'),
    path('eventos/tareas/', views.eventos_tareas_json, name='eventos_tareas_json'),
    path('eventos/personales/', views.eventos_personales_json, name='eventos_personales_json'),
    path('eventos/plantilla/crear/', views.crear_evento_plantilla, name='crear_evento_plantilla'),
    path('eventos/plantillas/', views.lista_eventos_plantilla, name='lista_eventos_plantilla'),
]

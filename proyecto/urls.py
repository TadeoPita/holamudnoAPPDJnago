# proyecto/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_proyectos, name='lista_proyectos'),
    path('crear/', views.crear_proyecto, name='crear_proyecto'),
    path('<int:proyecto_id>/', views.detalle_proyecto, name='detalle_proyecto'),
    path('<int:proyecto_id>/crear-tarea/',
         views.crear_tarea, name='crear_tarea'),
    path('<int:id>/editar/', views.editar_proyecto, name='editar_proyecto'),
    path('<int:id>/eliminar/', views.eliminar_proyecto, name='eliminar_proyecto'),
    
]

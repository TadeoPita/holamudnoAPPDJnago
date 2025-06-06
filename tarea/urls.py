
from django.urls import path

from proyecto.views import inicio
from tarea.forms import marcar_como_completada
from .views import (
    cambiar_color_columna,
    crear_columna,
    crear_etiqueta,
    eliminar_checklist_item,
    mover_tarea,
    tarea_detalle_modal,
    lista_tareas_usuario,
    editar_tarea,
    eliminar_tarea,
    agregar_checklist,
    agregar_comentario,
    completar_checklist_item,
    agregar_adjunto
)

urlpatterns = [
     path('', inicio, name='inicio'),  # ✅ esta línea es la clave
    path('<int:id>/detalle/', tarea_detalle_modal, name='tarea_detalle_modal'),
    path('mis-tareas/', lista_tareas_usuario, name='lista_tareas_usuario'),
    path('<int:id>/editar/', editar_tarea, name='editar_tarea'),
    path('<int:id>/eliminar/', eliminar_tarea, name='eliminar_tarea'),
    path('<int:tarea_id>/agregar-comentario/',
         agregar_comentario, name='agregar_comentario'),
    path('<int:tarea_id>/agregar-checklist/',
         agregar_checklist, name='agregar_checklist'),
    path('checklist/<int:item_id>/completar/',
         completar_checklist_item, name='completar_checklist_item'),
    path('columna/<int:columna_id>/color/',
         cambiar_color_columna, name='cambiar_color_columna'),

    path('tarea/<int:tarea_id>/agregar-adjunto/',
         agregar_adjunto, name='agregar_adjunto'),
    path('<int:tarea_id>/mover/', mover_tarea,
         name='mover_tarea'),  # ✅ Coma agregada
    path('proyecto/<int:proyecto_id>/crear-columna/',
         crear_columna, name='crear_columna'),
    path("tarea/checklist/<int:item_id>/eliminar/",
         eliminar_checklist_item, name="eliminar_checklist_item"),

    path('tarea/<int:tarea_id>/completar/',
         marcar_como_completada, name='marcar_como_completada'),

     path('etiqueta/crear/', crear_etiqueta, name='crear_etiqueta'),
]

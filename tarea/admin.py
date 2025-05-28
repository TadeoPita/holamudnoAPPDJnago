from django.contrib import admin
from .models import Columna, Tarea, ItemChecklist, Comentario, Adjunto

admin.site.register(Columna)

admin.site.register(ItemChecklist)
admin.site.register(Comentario)
admin.site.register(Adjunto)


class TareaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'asignado_a', 'fecha_creacion', 'fecha_limite', 'completada')
    list_filter = ('asignado_a', 'completada', 'columna')
    search_fields = ('titulo', 'descripcion', 'completada', 'fecha_creacion', 'fecha_limite')
    ordering = ('-fecha_creacion',)
    
admin.site.register(Tarea)
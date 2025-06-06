from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Columna, Tarea, ItemChecklist, Comentario, Adjunto


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 1
@admin.register(Columna)
class ColumnaAdmin(admin.ModelAdmin):
    list_display = ('nombre','proyecto')  # ⚠️ 'orden' removido

@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_creacion','get_etiquetas', 'completada','prioridad','columna')  # ⚠️ 'asignado_a', 'fecha_limite' removidos
    list_filter = ('completada','fecha_creacion', 'columna', 'prioridad', 'proyecto')
    search_fields = ('titulo', 'descripcion')
    ordering = ('-fecha_creacion',)
    list_display_links = ('titulo',)
    list_editable = ('completada',)
    readonly_fields = ('fecha_creacion',)
    #inlines = [ComentarioInline]
    def get_etiquetas(self, obj):
        return mark_safe(" ".join([
            f'<span style="background-color: {et.color}; color: white; padding: 3px 6px; border-radius: 3px;">{et.nombre}</span> '
            for et in obj.etiquetas.all()
        ]))
    get_etiquetas.short_description = "Etiquetas"

@admin.register(ItemChecklist)
class ItemChecklistAdmin(admin.ModelAdmin):
    list_display = ('tarea','completado')  # ⚠️ 'texto' removido

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('tarea','autor','fecha_creacion')  # ⚠️ 'usuario' removido

@admin.register(Adjunto)
class AdjuntoAdmin(admin.ModelAdmin):
    list_display = ('tarea', 'archivo','url','creado_por', 'fecha_creacion')  # ⚠️ 'subido_por', 'fecha_subida' removidos


# tarea/admin.py
from .models import Etiqueta

@admin.register(Etiqueta)
class EtiquetaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'color')

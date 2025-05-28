from django.contrib import admin
from .models import EventoPersonal

@admin.register(EventoPersonal)
class EventoPersonalAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'fecha_inicio', 'fecha_fin', 'usuario']
    list_filter = ['usuario', 'fecha_inicio']

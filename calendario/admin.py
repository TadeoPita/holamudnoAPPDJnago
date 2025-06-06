from django.contrib import admin
from .models import EventoPersonal

@admin.register(EventoPersonal)
class EventoPersonalAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'fecha_inicio', 'fecha_fin', 'usuario']
    list_filter = ['usuario', 'fecha_inicio']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Solo muestra los eventos del usuario logueado
        return qs.filter(usuario=request.user)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            # Bloquea el campo 'usuario' para que no lo cambien
            form.base_fields['usuario'].initial = request.user
            form.base_fields['usuario'].disabled = True
        return form

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is not None and obj.usuario != request.user:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is not None and obj.usuario != request.user:
            return False
        return True

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is not None and obj.usuario != request.user:
            return False
        return True


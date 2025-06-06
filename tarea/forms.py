from django import forms
from .models import Tarea
from .models import Comentario, ItemChecklist

from django import forms
from .models import Tarea
from .models import Adjunto
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse


class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = [
            'visible_para_todos', 'titulo', 'descripcion', 'prioridad',
            'fecha_vencimiento', 'completada', 'columna', 'asignado_a','puede_marcar_como_completada','etiquetas' 
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'columna': forms.Select(attrs={'class': 'form-control'}),
            'asignado_a': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'visible_para_todos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'completada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'etiquetas': forms.SelectMultiple(attrs={'class': 'form-control'}) ,
        }


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe un comentario...', 'rows': 2})
        }


class ChecklistForm(forms.ModelForm):
    class Meta:
        model = ItemChecklist
        fields = ['descripcion', 'asignado_a']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nuevo ítem del checklist'}),
            'asignado_a': forms.Select(attrs={'class': 'form-control'}),
        }


class AdjuntoForm(forms.ModelForm):
    class Meta:
        model = Adjunto
        fields = ['archivo', 'url']
        widgets = {
            'archivo': forms.ClearableFileInput(attrs={
                'class': 'form-control bg-dark text-white border-secondary'
            }),
            'url': forms.URLInput(attrs={
                'placeholder': 'https://ejemplo.com/archivo',
                'class': 'form-control bg-dark text-white border-secondary'
            })
        }


@require_POST
@login_required
def marcar_como_completada(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)

    if request.user not in tarea.puede_marcar_como_completada.all() and not request.user.is_staff:
        return HttpResponseForbidden("No tenés permiso para completar esta tarea.")

    tarea.completada = True
    tarea.completada_por = request.user
    tarea.save()
    return JsonResponse({"ok": True})

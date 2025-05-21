from django import forms
from .models import Tarea
from .models import Comentario, ItemChecklist

from django import forms
from .models import Tarea
from .models import Adjunto

class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = [
            'visible_para_todos', 'titulo', 'descripcion', 'prioridad',
            'fecha_vencimiento', 'completada', 'columna', 'asignado_a'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'columna': forms.Select(attrs={'class': 'form-control'}),
            'asignado_a': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'visible_para_todos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'completada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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



from django import forms
from .models import Adjunto

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

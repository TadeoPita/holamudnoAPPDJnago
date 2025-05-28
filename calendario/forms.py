from django import forms
from .models import EventoPersonal

class EventoPersonalForm(forms.ModelForm):
    class Meta:
        model = EventoPersonal
        fields = ['titulo', 'fecha_inicio', 'fecha_fin', 'color']

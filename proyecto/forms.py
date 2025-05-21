from django import forms
from .models import Proyecto
from django.contrib.auth.models import User

class ProyectoForm(forms.ModelForm):
    usuarios_asignados = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion', 'usuarios_asignados']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
        }

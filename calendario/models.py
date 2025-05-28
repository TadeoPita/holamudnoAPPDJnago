from django.db import models
from django.contrib.auth.models import User

class EventoPersonal(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    color = models.CharField(max_length=7, default="#70C1B3")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.titulo} ({self.fecha_inicio.date()})"

from django.db import models
from django.contrib.auth.models import User

class EventoPersonal(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    color = models.CharField(max_length=20, default="#FFB700")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

class EventoPlantilla(models.Model):
    titulo = models.CharField(max_length=200)
    color = models.CharField(max_length=20, default="#6c63ff")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

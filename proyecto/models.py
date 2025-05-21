from django.db import models
from django.contrib.auth.models import User

class Proyecto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    usuarios_asignados = models.ManyToManyField(User, related_name='proyectos')

    def __str__(self):
        return self.nombre

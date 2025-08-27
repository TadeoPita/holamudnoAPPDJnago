from django.db import models
from django.contrib.auth.models import User

class EventoPersonal(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
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
    
class SeguidoresHistorico(models.Model):
    instagram_id = models.CharField(max_length=50)
    fecha = models.DateField()
    seguidores = models.PositiveIntegerField()

    class Meta:
        unique_together = ('instagram_id', 'fecha')
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.instagram_id} - {self.fecha} - {self.seguidores} seguidores"
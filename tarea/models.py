from django.db import models
from django.contrib.auth.models import User
from proyecto.models import Proyecto

class Columna(models.Model):
    nombre = models.CharField(max_length=100)
    color = models.CharField(max_length=7)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='columnas')

    def __str__(self):
        return f"{self.nombre} ({self.proyecto.nombre})"

class Tarea(models.Model):
    PRIORIDADES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ]
    visible_para_todos = models.BooleanField(default=False)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    completada = models.BooleanField(default=False)
    columna = models.ForeignKey('Columna', on_delete=models.CASCADE, related_name='tareas')
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='tareas')
    asignado_a = models.ManyToManyField(User, related_name='tareas_asignadas')
    modificado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tareas_modificadas')

    def __str__(self):
        return self.titulo

class ItemChecklist(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='checklist')
    descripcion = models.CharField(max_length=255)
    completado = models.BooleanField(default=False)
    asignado_a = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='checklist_creados')
    completado_fecha = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.descripcion


class Comentario(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.autor} - {self.texto[:30]}..."

class Adjunto(models.Model):
    tarea = models.ForeignKey('Tarea', on_delete=models.CASCADE, related_name='adjuntos')
    archivo = models.FileField(upload_to='adjuntos/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.archivo.name if self.archivo else self.url
# proyecto/views.py
from urllib import request
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from calendario import models
from .models import  Proyecto
from .forms import ProyectoForm
from tarea.forms import TareaForm  # ✅ Así está bien
from tarea.models import Columna, Tarea
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from tarea.models import Tarea
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q


@login_required
def lista_proyectos(request):
    proyectos = Proyecto.objects.filter(
        usuarios_asignados=request.user) | Proyecto.objects.filter(usuarios_asignados=None)
    return render(request, 'proyecto/lista_proyectos.html', {'proyectos': proyectos})


@login_required
def crear_proyecto(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save()
            return redirect('lista_proyectos')
    else:
        form = ProyectoForm()
    return render(request, 'proyecto/crear_proyecto.html', {'form': form})

from django.db.models import Case, When, IntegerField
@login_required
def detalle_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    if request.user not in proyecto.usuarios_asignados.all():
        return render(request, '403.html')

    request.session['proyecto_actual_id'] = proyecto_id
    columnas = proyecto.columnas.all().prefetch_related('tareas__asignado_a', 'tareas__comentarios')

    orden = request.GET.get("orden")
    completadas = request.GET.get("completadas")
    asignadas = request.GET.get("asignadas")

    for columna in columnas:
        tareas = columna.tareas.all()

        if asignadas == "true":
            tareas = tareas.filter(asignado_a=request.user)

        if completadas == "true":
            tareas = tareas.filter(completada=True)
        elif completadas == "false":
            tareas = tareas.filter(completada=False)

        if orden == "recientes":
            tareas = tareas.order_by("-fecha_creacion")
        elif orden == "antiguas":
            tareas = tareas.order_by("fecha_creacion")
        elif orden == "prioridad":
            prioridad_orden = Case(
                When(prioridad="alta", then=1),
                When(prioridad="media", then=2),
                When(prioridad="baja", then=3),
                output_field=IntegerField()
            )
            tareas = tareas.order_by(prioridad_orden)

        columna.tareas_filtradas = tareas

    return render(request, 'proyecto/detalle_proyecto.html', {
        'proyecto': proyecto,
        'columnas': columnas
    })


@login_required
def crear_tarea(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    if request.user not in proyecto.usuarios_asignados.all():
        return HttpResponseForbidden("No autorizado")

    if request.method == 'POST':
        form = TareaForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.proyecto = proyecto
            tarea.modificado_por = request.user
            tarea.save()
            form.save_m2m()
            return redirect('detalle_proyecto', proyecto_id=proyecto.id)
    else:
        form = TareaForm()
        form.fields['columna'].queryset = proyecto.columnas.all()

    return render(request, 'proyecto/crear_tarea.html', {
        'form': form,
        'proyecto': proyecto
    })


@login_required
def editar_proyecto(request, id):
    proyecto = get_object_or_404(Proyecto, id=id)

    if not request.user.is_staff:
        return HttpResponseForbidden("No tenés permiso para editar este proyecto.")

    if request.method == 'POST':
        form = ProyectoForm(request.POST, instance=proyecto)
        if form.is_valid():
            form.save()
            return redirect('detalle_proyecto', id)
    else:
        form = ProyectoForm(instance=proyecto)

    return render(request, 'proyecto/editar_proyecto.html', {
        'form': form,
        'proyecto': proyecto
    })


@login_required
def eliminar_proyecto(request, id):
    proyecto = get_object_or_404(Proyecto, id=id)

    if not request.user.is_staff:
        return HttpResponseForbidden("No tenés permiso para eliminar este proyecto.")

    if request.method == 'POST':
        proyecto.delete()
        return redirect('lista_proyectos')

    return render(request, 'proyecto/confirmar_eliminacion.html', {
        'proyecto': proyecto
    })

from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta, date
from django.db.models import Count, Q
from tarea.models import Tarea
from proyecto.models import Proyecto
from calendario.models import EventoPersonal

def inicio(request):
    user = request.user
    hoy = timezone.now().date()
    semana = hoy + timedelta(days=7)

    # Obtener todas las tareas
    tareas = Tarea.objects.select_related("proyecto", "columna") \
                          .prefetch_related("etiquetas", "asignado_a") \
                          .all()

    # Filtros desde query params
    proyecto_id = request.GET.get('proyecto')
    prioridad = request.GET.get('prioridad')
    orden = request.GET.get('orden')
    completadas = request.GET.get('completadas')
    asignadas = request.GET.get('asignadas')

    if proyecto_id:
        tareas = tareas.filter(proyecto_id=proyecto_id)

    if prioridad:
        tareas = tareas.filter(prioridad=prioridad)

    if completadas == "true":
        tareas = tareas.filter(completada=True)
    elif completadas == "false":
        tareas = tareas.filter(completada=False)

    if asignadas == "true":
        tareas = tareas.filter(asignado_a=user)

    if orden == "recientes":
        tareas = tareas.order_by("-fecha_vencimiento")
    elif orden == "antiguas":
        tareas = tareas.order_by("fecha_vencimiento")
    elif orden == "prioridad":
        tareas = tareas.order_by("prioridad")  # campo tipo choices

    # Separar tareas completadas y pendientes
    tareas_pendientes = tareas.filter(completada=False)
    tareas_completadas = tareas.filter(completada=True)

    # Paginación
    pendientes_cant = int(request.GET.get("pendientes_cant", 5))
    completadas_cant = int(request.GET.get("completadas_cant", 5))
    pendientes_page = request.GET.get("pendientes_page")
    completadas_page = request.GET.get("completadas_page")

    pendientes_paginator = Paginator(tareas_pendientes, pendientes_cant)
    completadas_paginator = Paginator(tareas_completadas, completadas_cant)

    tareas_pendientes_paginadas = pendientes_paginator.get_page(pendientes_page)
    tareas_completadas_paginadas = completadas_paginator.get_page(completadas_page)

    # Estadísticas
    total_tareas = tareas.count()
    tareas_completadas_count = tareas_completadas.count()
    tareas_pendientes_count = tareas_pendientes.count()
    tareas_semana = tareas.filter(fecha_vencimiento__range=(hoy, semana)).count()

    # Proyectos con tareas (asignadas al usuario)
    proyectos_con_tareas = tareas.filter(asignado_a=user).values("proyecto__nombre").annotate(
        pendientes=Count("id", filter=Q(completada=False)),
        completadas=Count("id", filter=Q(completada=True))
    )

    eventos = EventoPersonal.objects.filter(usuario=user)

    context = {
        "tareas_pendientes_paginadas": tareas_pendientes_paginadas,
        "tareas_completadas_paginadas": tareas_completadas_paginadas,
        "tareas_proximas": tareas_pendientes.order_by("fecha_vencimiento")[:10],
        "tareas_completadas": tareas_completadas.order_by("-fecha_vencimiento")[:10],
        "pendientes_cant": pendientes_cant,
        "completadas_cant": completadas_cant,
        "proyectos": Proyecto.objects.all(),
        "proyectos_con_tareas": proyectos_con_tareas,
        "tareas_completadas_count": tareas_completadas_count,
        "tareas_pendientes_count": tareas_pendientes_count,
        "tareas_semana": tareas_semana,
        "total_tareas": total_tareas,
        "eventos": eventos,
    }

    return render(request, "inicio.html", context)
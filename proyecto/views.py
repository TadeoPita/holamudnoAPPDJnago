# proyecto/views.py
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .models import Proyecto
from .forms import ProyectoForm
from tarea.forms import TareaForm  # ✅ Así está bien
from tarea.models import Columna, Tarea
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from tarea.models import Tarea
from django.utils import timezone
from datetime import timedelta

@login_required
def lista_proyectos(request):
    proyectos = Proyecto.objects.filter(usuarios_asignados=request.user) | Proyecto.objects.filter(usuarios_asignados=None)
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

@login_required
def detalle_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    if request.user not in proyecto.usuarios_asignados.all():
        return render(request, '403.html')

    columnas = proyecto.columnas.all().prefetch_related('tareas')
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


@login_required
def inicio(request):
    hoy = timezone.now().date()
    tareas_proximas = Tarea.objects.filter(
        fecha_vencimiento__gte=hoy,
        fecha_vencimiento__lte=hoy + timedelta(days=7),
        completada=False
    ).filter(
        asignado_a=request.user
    ) | Tarea.objects.filter(
        visible_para_todos=True,
        completada=False
    )

    tareas_completadas = Tarea.objects.filter(
        completada=True
    ).order_by('-fecha_vencimiento')[:5]

    return render(request, 'inicio.html', {
        'tareas_proximas': tareas_proximas.distinct(),
        'tareas_completadas': tareas_completadas,
    })
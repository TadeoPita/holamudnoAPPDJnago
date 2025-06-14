from django.middleware.csrf import get_token
from django.http import JsonResponse
from .forms import ComentarioForm, ChecklistForm
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from calendario import models
from .models import Tarea, Columna, Comentario, ItemChecklist, Adjunto
from proyecto.models import Proyecto
from .forms import TareaForm
from django.http import HttpResponseForbidden

# Modal de detalle de tarea
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q

from .models import Tarea, Columna, Comentario, ItemChecklist, Adjunto
from .forms import TareaForm, ComentarioForm, ChecklistForm
from proyecto.models import Proyecto


@login_required
def tarea_detalle_modal(request, id):
    tarea = get_object_or_404(Tarea, id=id)

    if not tarea.visible_para_todos and request.user not in tarea.proyecto.usuarios_asignados.all():
        return HttpResponseForbidden()

    checklist_visibles = (
        tarea.checklist.all() if request.user.is_staff
        else tarea.checklist.filter(
            Q(asignado_a=request.user) |
            (Q(asignado_a__isnull=True) & (Q(tarea__visible_para_todos=True) | Q(tarea__proyecto__usuarios_asignados=request.user)))
        ).distinct()
    )

    return render(request, 'tarea/modals/tarea_detalle.html', {
        'tarea': tarea,
        'checklist': checklist_visibles,
        'comentarios': tarea.comentarios.all(),
        'comentario_form': ComentarioForm(),
        'checklist_form': ChecklistForm(),
        'adjunto_form': AdjuntoForm(),
    })
# Listado general de tareas (opcional)


@login_required
def lista_tareas_usuario(request):
    tareas = Tarea.objects.filter(asignado_a=request.user)
    return render(request, 'tarea/lista_tareas.html', {'tareas': tareas})

# Editar tarea


@login_required
def editar_tarea(request, id):
    tarea = get_object_or_404(Tarea, id=id)
    proyecto = tarea.proyecto

    if request.user not in proyecto.usuarios_asignados.all():
        return HttpResponseForbidden("No autorizado")

    if request.method == 'POST':
        form = TareaForm(request.POST, instance=tarea)
        if form.is_valid():
           tarea = form.save(commit=False)
           tarea.modificado_por = request.user
           tarea.save()
           form.save_m2m()  # << ESTA LÍNEA es la clave para asignado_a (ManyToMany)
           return redirect('detalle_proyecto', proyecto_id=proyecto.id)
    else:
        form = TareaForm(instance=tarea)
        form.fields['columna'].queryset = proyecto.columnas.all()

    return render(request, 'tarea/editar_tarea.html', {'form': form, 'tarea': tarea})

# Eliminar tarea


@login_required
def eliminar_tarea(request, id):
    tarea = get_object_or_404(Tarea, id=id)
    proyecto = tarea.proyecto

    if request.user not in proyecto.usuarios_asignados.all():
        return HttpResponseForbidden("No autorizado")

    if request.method == 'POST':
        tarea.delete()
        return redirect('detalle_proyecto', proyecto_id=proyecto.id)

    return render(request, 'tarea/eliminar_tarea.html', {'tarea': tarea})


@login_required
def agregar_comentario(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)

    if request.user not in tarea.proyecto.usuarios_asignados.all() and not tarea.visible_para_todos:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.tarea = tarea
            comentario.autor = request.user
            comentario.save()
            html = render_to_string(
                'tarea/components/comentario_item.html', {'comentario': comentario})
            return HttpResponse(html)
    return HttpResponse(status=400)


@login_required
def agregar_checklist(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)

    if request.user not in tarea.proyecto.usuarios_asignados.all() and not tarea.visible_para_todos:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = ChecklistForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.tarea = tarea
            item.creado_por = request.user
            # Si no se seleccionó usuario, queda en None (público)
            item.asignado_a = form.cleaned_data.get('asignado_a')
            item.save()
            html = render_to_string(
                'tarea/components/checklist_item.html', {'item': item})
            return HttpResponse(html)
    return HttpResponse(status=400)


@login_required
def completar_checklist_item(request, item_id):
    item = get_object_or_404(ItemChecklist, id=item_id)

    puede_completar = (
        request.user.is_staff or
        (item.asignado_a == request.user)
    )

    if not puede_completar:
        return HttpResponseForbidden("No tenés permiso para completar este ítem")

    item.completado = not item.completado
    item.completado_fecha = timezone.now() if item.completado else None
    item.save()

    html = render_to_string("tarea/components/checklist_item.html",
                            {"item": item, "csrf_token": get_token(request)})
    return HttpResponse(html)


@login_required
def cambiar_color_columna(request, columna_id):
    if not request.user.is_staff:
        return redirect('lista_proyectos')

    columna = get_object_or_404(Columna, id=columna_id)
    if request.method == 'POST':
        nuevo_color = request.POST.get('color')
        if nuevo_color:
            columna.color = nuevo_color
            columna.save()
    return redirect('detalle_proyecto', proyecto_id=columna.proyecto.id)




from .forms import AdjuntoForm

from .forms import AdjuntoForm
from django.template.loader import render_to_string

@login_required
def agregar_adjunto(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)

    if request.user not in tarea.proyecto.usuarios_asignados.all() and not request.user.is_staff:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = AdjuntoForm(request.POST, request.FILES)
        if form.is_valid():
            adjunto = form.save(commit=False)
            adjunto.tarea = tarea
            adjunto.creado_por = request.user
            adjunto.save()

            html = render_to_string("tarea/components/adjunto_item.html", {"adj": adjunto})
            return HttpResponse(html)
        else:
            return HttpResponse(f"<pre>{form.errors}</pre>", status=400)

    return HttpResponse(status=400)

from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
@login_required
def mover_tarea(request, tarea_id):
    if request.method != 'POST':
        return HttpResponseForbidden("Método no permitido")

    tarea = get_object_or_404(Tarea, id=tarea_id)

    if not tarea.visible_para_todos and request.user not in tarea.proyecto.usuarios_asignados.all() and not request.user.is_staff:
        return HttpResponseForbidden("No tenés permiso para mover esta tarea")

    data = json.loads(request.body)
    nueva_columna_id = data.get('columna_id')
    nueva_columna = get_object_or_404(Columna, id=nueva_columna_id)

    tarea.columna = nueva_columna
    tarea.save()

    return JsonResponse({"ok": True})

@login_required
def crear_columna(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if not request.user.is_staff:
        return HttpResponseForbidden()

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        color = request.POST.get('color') or '#ffffff'
        if nombre:
            Columna.objects.create(nombre=nombre, color=color, proyecto=proyecto)
    return redirect('detalle_proyecto', proyecto_id=proyecto.id)



@login_required
def eliminar_checklist_item(request, item_id):
    item = get_object_or_404(ItemChecklist, id=item_id)

    if not (request.user.is_staff or item.creado_por == request.user):
        return HttpResponseForbidden("No autorizado para eliminar este ítem")

    item.delete()
    return HttpResponse(status=204)  # Solo elimina el nodo

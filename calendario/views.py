from datetime import timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import EventoPersonal
from tarea.models import Tarea
import json


@login_required
def mi_calendario(request):
    return render(request, 'calendario/mi_calendario.html')


@require_POST
@login_required
def crear_evento_personal(request):
    titulo = request.POST.get('titulo')
    descripcion = request.POST.get('descripcion', '')
    fecha_inicio = request.POST.get('fecha_inicio')
    fecha_fin = request.POST.get('fecha_fin') or fecha_inicio
    color = request.POST.get('color', '#70C1B3')

    if titulo and fecha_inicio:
        EventoPersonal.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            color=color,
            usuario=request.user
        )
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False})


@require_POST
@login_required
@csrf_exempt
def actualizar_evento_personal(request, evento_id):
    try:
        evento = EventoPersonal.objects.get(id=evento_id, usuario=request.user)

        if request.content_type == 'application/json':
            data = json.loads(request.body)
            evento.fecha_inicio = data.get('start')
            evento.fecha_fin = data.get('end') or data.get('start')
        else:
            evento.titulo = request.POST.get('titulo')
            evento.descripcion = request.POST.get('descripcion', '')
            evento.fecha_inicio = request.POST.get('fecha_inicio')
            evento.fecha_fin = request.POST.get(
                'fecha_fin') or evento.fecha_inicio
            evento.color = request.POST.get('color', '#70C1B3')

        evento.save()
        return JsonResponse({'ok': True})
    except EventoPersonal.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'No encontrado'})


@require_POST
@login_required
def eliminar_evento_personal(request, evento_id):
    try:
        evento = EventoPersonal.objects.get(id=evento_id, usuario=request.user)
        evento.delete()
        return JsonResponse({'ok': True})
    except EventoPersonal.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'No encontrado'})


@login_required
def eventos_personales_json(request):
    eventos = EventoPersonal.objects.filter(usuario=request.user)
    data = [{
        'id': e.id,
        'title': e.titulo,
        'start': e.fecha_inicio.isoformat(),
        'end': e.fecha_fin.isoformat(),
        'color': e.color,
        'descripcion': e.descripcion
    } for e in eventos]
    return JsonResponse(data, safe=False)


@login_required
def eventos_tareas_json(request):
    tareas = Tarea.objects.filter(completada=False)
    if not request.user.is_staff:
        tareas = tareas.filter(asignado_a=request.user) | tareas.filter(
            visible_para_todos=True)

    tareas = tareas.distinct()

    data = [{
        'title': f"Tarea: {t.titulo}",
        'start': t.fecha_vencimiento.isoformat(),
        'end': (t.fecha_vencimiento + timedelta(days=1)).isoformat(),
        'color': '#66c7ff',
        'id': t.id
    } for t in tareas if t.fecha_vencimiento]
    return JsonResponse(data, safe=False)

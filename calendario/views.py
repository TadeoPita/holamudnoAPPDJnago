from datetime import timedelta
import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import EventoPersonal, EventoPlantilla
from tarea.models import Tarea


@login_required
def mi_calendario(request):
    return render(request, 'calendario/mi_calendario.html')


@require_POST
@login_required
@csrf_exempt
def crear_evento_personal(request):
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        titulo = data.get('titulo')
        descripcion = data.get('descripcion', '')
        fecha_inicio = str(data.get('fecha_inicio'))
        fecha_fin = str(data.get('fecha_fin') or fecha_inicio)
        color = data.get('color', "#27FC4B")

        if not titulo or not fecha_inicio:
            return JsonResponse({'ok': False, 'error': 'Faltan campos requeridos'})

        try:
            fecha_inicio_date = timezone.datetime.fromisoformat(fecha_inicio).date()
            fecha_fin_date = timezone.datetime.fromisoformat(fecha_fin).date()
        except ValueError:
            return JsonResponse({'ok': False, 'error': 'Formato de fecha inválido'})

        EventoPersonal.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            fecha_inicio=fecha_inicio_date,
            fecha_fin=fecha_fin_date,
            color=color,
            usuario=request.user
        )

        return JsonResponse({'ok': True})

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@require_POST
@login_required
@csrf_exempt
def actualizar_evento_personal(request, evento_id):
    try:
        evento = EventoPersonal.objects.get(id=evento_id, usuario=request.user)

        # 👇 Manejo de solicitud JSON (usado por FullCalendar y tu formulario modal)
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            start = str(data.get('start'))
            end = str(data.get('end') or start)

            if not start or start == 'None':
                return JsonResponse({'ok': False, 'error': 'Fecha de inicio inválida'})
            if not end or end == 'None':
                return JsonResponse({'ok': False, 'error': 'Fecha de fin inválida'})

            try:
                evento.fecha_inicio = timezone.datetime.fromisoformat(start).date()
                evento.fecha_fin = timezone.datetime.fromisoformat(end).date()
            except ValueError:
                return JsonResponse({'ok': False, 'error': 'Formato de fecha inválido'})

            # ✅ Nuevos campos incluidos en edición por JSON
            evento.titulo = data.get('titulo', evento.titulo)
            evento.descripcion = data.get('descripcion', evento.descripcion)
            evento.color = data.get('color', evento.color)

        else:
            # 📝 Alternativa para formulario tradicional (POST normal)
            evento.titulo = request.POST.get('titulo')
            evento.descripcion = request.POST.get('descripcion', '')
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')

            if not fecha_inicio or fecha_inicio == 'None':
                return JsonResponse({'ok': False, 'error': 'Fecha de inicio inválida'})
            if not fecha_fin or fecha_fin == 'None':
                return JsonResponse({'ok': False, 'error': 'Fecha de fin inválida'})

            try:
                evento.fecha_inicio = timezone.datetime.fromisoformat(fecha_inicio).date()
                evento.fecha_fin = timezone.datetime.fromisoformat(fecha_fin).date()
            except ValueError:
                return JsonResponse({'ok': False, 'error': 'Formato de fecha inválido'})

            evento.color = request.POST.get('color', "#FFBE18")

        evento.save()
        return JsonResponse({'ok': True})

    except EventoPersonal.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Evento no encontrado'})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})
    
    
@require_POST
@login_required
@csrf_exempt
def eliminar_evento_personal(request, evento_id):
    try:
        evento = EventoPersonal.objects.get(id=evento_id, usuario=request.user)
        evento.delete()
        return JsonResponse({'ok': True})
    except EventoPersonal.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'No encontrado'})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required
def eventos_personales_json(request):
    eventos = EventoPersonal.objects.filter(usuario=request.user)

    data = []
    for e in eventos:
        if not e.fecha_inicio or not e.fecha_fin:
            continue

        data.append({
            'title': e.titulo,
            'start': e.fecha_inicio.isoformat(),
            'end': (e.fecha_fin + timedelta(days=1)).isoformat(),  # FullCalendar requiere end exclusivo
            'color': e.color or "#FFD91B",
            'id': e.id,
            'descripcion': e.descripcion or '',
            'allDay': True
        })

    return JsonResponse(data, safe=False)


@login_required
def eventos_tareas_json(request):
    tareas = (
        Tarea.objects.filter(completada=False, asignado_a=request.user)
        | Tarea.objects.filter(visible_para_todos=True)
    ).distinct()

    data = [
        {
            'title': f"Tarea: {t.titulo}",
            'start': t.fecha_vencimiento.isoformat(),
            'end': (t.fecha_vencimiento + timedelta(days=1)).isoformat(),
            'color': "#0e0e0e",
            'id': f'tarea-{t.id}',
            'allDay': True
        }
        for t in tareas if t.fecha_vencimiento
    ]

    return JsonResponse(data, safe=False)


@login_required
def plantillas_eventos_rapidos(request):
    plantillas = EventoPlantilla.objects.filter(usuario=request.user)
    data = [{
        'title': p.titulo,
        'color': p.color
    } for p in plantillas]
    return JsonResponse(data, safe=False)


@require_POST
@login_required
@csrf_exempt
def crear_evento_plantilla(request):
    try:
        data = json.loads(request.body)
        evento = EventoPlantilla.objects.create(
            titulo=data['titulo'],
            color=data.get('color', '#6c63ff'),
            usuario=request.user
        )
        return JsonResponse({'ok': True, 'evento': {'titulo': evento.titulo, 'color': evento.color}})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required
def lista_eventos_plantilla(request):
    plantillas = EventoPlantilla.objects.filter(usuario=request.user)
    data = [{'titulo': p.titulo, 'color': p.color} for p in plantillas]
    return JsonResponse(data, safe=False)

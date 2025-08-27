from collections import defaultdict
from datetime import datetime, timedelta
from email.utils import parsedate
import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import EventoPersonal, EventoPlantilla, SeguidoresHistorico
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


import requests
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from datetime import datetime, timedelta
import random

GRAPH_API_URL = 'https://graph.facebook.com/v23.0'
ACCESS_TOKEN = settings.META_ACCESS_TOKEN

@login_required
def cuentas(request):
    url = f"{GRAPH_API_URL}/me/accounts"
    params = {
        'access_token': settings.META_ACCESS_TOKEN
    }
    response = requests.get(url, params=params)

    cuentas = []
    if response.status_code == 200:
        data = response.json()
        for page in data.get('data', []):
            # Aquí, primero pides el instagram_business_account
            page_id = page.get('id')
            ig_url = f"{GRAPH_API_URL}/{page_id}?fields=instagram_business_account&access_token={settings.META_ACCESS_TOKEN}"
            ig_response = requests.get(ig_url)
            ig_data = ig_response.json()

            instagram_account = ig_data.get('instagram_business_account', {})

            if instagram_account:
                cuentas.append({
                    'name': page.get('name'),
                    'id': instagram_account.get('id'),  # Aquí ya tienes el Instagram ID
                    'page_id': page.get('id')
                })
    else:
        print("Error al obtener las cuentas:", response.text)

    context = {
        'cuentas': cuentas
    }
    return render(request, 'instagram/cuentas.html', context)


from django.core.paginator import Paginator

@login_required
def dashboard(request, instagram_id):
    """
    Dashboard completo con métricas, demografía y publicaciones.
    """

    # ----------------- Manejo Seguro de Fechas -----------------
    fecha_inicio = request.GET.get('desde')
    fecha_fin = request.GET.get('hasta')

    try:
        fecha_inicio = parsedate(fecha_inicio)
        fecha_fin = parsedate(fecha_fin)
    except:
        fecha_inicio = None
        fecha_fin = None

    if not fecha_inicio or not fecha_fin:
        hoy = datetime.today().date()
        fecha_fin = hoy
        fecha_inicio = hoy - timedelta(days=30)

    fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
    fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')

    # ----------------- Datos Generales de la Cuenta -----------------
    url = f"{GRAPH_API_URL}/{instagram_id}"
    params = {
        'fields': 'biography,followers_count,follows_count,id,media_count,name,profile_picture_url,username,website',
        'access_token': settings.META_ACCESS_TOKEN
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(response.text)
        raise Http404("Error al obtener información de la cuenta")

    data = response.json()

    # ----------------- Métricas de Insights Generales -----------------
    insights_metrics = [
        'impressions', 'reach', 'profile_views', 'email_contacts', 'phone_call_clicks',
        'text_message_clicks', 'get_directions_clicks', 'website_clicks',
        'audience_city', 'audience_country', 'audience_gender_age'
    ]
    insights_url = f"{GRAPH_API_URL}/{instagram_id}/insights"
    insights_params = {
        'metric': ','.join(insights_metrics),
        'period': 'lifetime',
        'since': fecha_inicio_str,
        'until': fecha_fin_str,
        'access_token': settings.META_ACCESS_TOKEN
    }
    insights_response = requests.get(insights_url, params=insights_params)

    insights_data = {}
    if insights_response.status_code == 200:
        for metric in insights_response.json().get('data', []):
            name = metric.get('name')
            values = metric.get('values', [])
            if values:
                insights_data[name] = values[0].get('value', {})

    # ----------------- Procesamiento de Demografía -----------------
    paises = []
    ciudades = []
    genero_edad = []

    if insights_data.get('audience_country'):
        paises = sorted(insights_data['audience_country'].items(), key=lambda x: x[1], reverse=True)

    if insights_data.get('audience_city'):
        ciudades = sorted(insights_data['audience_city'].items(), key=lambda x: x[1], reverse=True)

    if insights_data.get('audience_gender_age'):
        genero_edad = sorted(insights_data['audience_gender_age'].items(), key=lambda x: x[1], reverse=True)

    total_audiencia = sum(insights_data.get('audience_country', {}).values()) or 1  # Para evitar división por 0

    paises_porcentaje = [
        (pais, round((cantidad / total_audiencia) * 100, 2))
        for pais, cantidad in paises
    ]

    genero_porcentaje = [
        (grupo, round((cantidad / total_audiencia) * 100, 2))
        for grupo, cantidad in genero_edad
    ]

    # ----------------- Publicaciones -----------------
    media_url = f"{GRAPH_API_URL}/{instagram_id}/media"
    media_params = {
        'fields': 'id,caption,media_type,media_url,timestamp,like_count,comments_count',
        'limit': 20,
        'access_token': settings.META_ACCESS_TOKEN
    }
    media_response = requests.get(media_url, params=media_params)

    publicaciones = []
    if media_response.status_code == 200:
        publicaciones = media_response.json().get('data', [])

    for post in publicaciones:
        post_id = post.get('id')
        post_metrics = ['impressions', 'reach', 'engagement', 'saved', 'video_views']
        post_metrics_url = f"{GRAPH_API_URL}/{post_id}/insights"
        post_metrics_params = {
            'metric': ','.join(post_metrics),
            'access_token': settings.META_ACCESS_TOKEN
        }
        metrics_response = requests.get(post_metrics_url, params=post_metrics_params)
        metrics_data = {}
        if metrics_response.status_code == 200:
            for metric in metrics_response.json().get('data', []):
                metrics_data[metric.get('name')] = metric.get('values', [{}])[0].get('value', 0)
        post['metrics'] = metrics_data

    # ----------------- Paginación -----------------
    paginator = Paginator(publicaciones, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'cuenta': data,
        'insights': insights_data,
        'paises': paises_porcentaje,
        'genero': genero_porcentaje,
        'ciudades': ciudades,
        'media': page_obj,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    }
    return render(request, 'instagram/dashboard.html', context)
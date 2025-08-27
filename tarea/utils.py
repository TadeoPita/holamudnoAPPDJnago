# tarea/utils.py

from django.core.mail import send_mail
from django.conf import settings

def notificar_tarea_evento(tarea, accion, usuario_realizador):
    asunto = f"Tarea actualizada: {tarea.titulo}"
    mensaje = f"""
Hola 👋,

La tarea "{tarea.titulo}" ha sido {accion} por {usuario_realizador.get_full_name() or usuario_realizador.username}.

📌 Proyecto: {tarea.proyecto.nombre}
📁 Columna actual: {tarea.columna.nombre}
⚡ Prioridad: {tarea.get_prioridad_display()}
📅 Fecha de vencimiento: {tarea.fecha_vencimiento or 'No definida'}

Podés ver la tarea en tu panel de tareas.
"""

    destinatarios = [u.email for u in tarea.asignado_a.all() if u.email]

    if destinatarios:
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            destinatarios,
            fail_silently=False,
        )

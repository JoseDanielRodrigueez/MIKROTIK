# Tareas asincronas para evitar que la GUI dependa de la respuesta del servidor
# y se bloquee mientras se ejecutan procesos largos

# notificaciones/tasks.py
from celery import shared_task
from . import services


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name='notificaciones.enviar_notificacion',
)
def enviar_notificacion_task(self, destinatario, asunto, mensaje, remitente=None):
    """
    Tarea Celery que envuelve el envío real.
    """
    try:
        exito = services.enviar_notificacion(destinatario, asunto, mensaje, remitente)
        return {"status": "ok" if exito else "failed"}
    except Exception as exc:
        print(f"Error en enviar_notificacion_task: {exc}")
        raise self.retry(exc=exc)


@shared_task(name='notificaciones.notificar_pago_exitoso')
def notificar_pago_exitoso_task(cliente_email, nombre_cliente, monto, referencia):
    services.notificar_pago_exitoso(cliente_email, nombre_cliente, monto, referencia)
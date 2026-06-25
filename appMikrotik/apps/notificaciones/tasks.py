# Tareas asincronas para evitar que la GUI dependa de la respuesta del servidor
# y se bloquee mientras se ejecutan procesos largos
# SOLO ENVIOS ASINCRONOS

from celery import shared_task, Task
from . import services
from .logs_utils import registrar_log_notificacion

class RetryTask(Task):
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3, "countdown": 60}


@shared_task(bind=True, base=RetryTask, name='notificaciones.enviar_correo')
def enviar_correo_task(self, email_cliente, asunto, mensaje, remitente=None):
    """Gestiona la tarea asincrona para enviar un correo generico"""
    try:
        exito = services.enviar_correo(email_cliente, asunto, mensaje, remitente)
        return {"status": "OK" if exito else "FAILED"}
    except Exception as exc:
        raise


@shared_task(bind=True, base=RetryTask, name='notificaciones.notificar_pago_exitoso')
def pago_exitoso_task(self, email_cliente, nombre_cliente, monto, pendiente, fecha):
    """Gestiona la tarea asincrona para notificar el pgo exitoso"""
    try:
        exito = services.notificar_pago_exitoso(nombre_cliente, email_cliente, monto, pendiente, fecha)
        registrar_log_notificacion(email_cliente, services.AsuntosNotificaciones.PAGO_EXITOSO, exito)
        return {"status": "OK" if exito else "FAILED"}
    except Exception as exc:
        # capturamos algun error inesperado
        registrar_log_notificacion(
            email_cliente,
            services.AsuntosNotificaciones.PAGO_EXITOSO,
            False, 
            f"Excep: {exc}"
        )
        raise

@shared_task(bind=True, base=RetryTask, name='notificaciones.bienvenida')
def bienvenida_task(self, nombre_cliente, email_cliente, nombre_plan, vel_sub, vel_baj):
    "gestiona la tarea asincrona para notificar la bienvenida al usuario al registrarse"
    try:
        exito = services.notificar_bienvenida(nombre_cliente, email_cliente, nombre_plan, vel_sub, vel_baj)
        registrar_log_notificacion(email_cliente, services.AsuntosNotificaciones.BIENVENIDA, exito)
        return {"status": "OK" if exito else "FAILED"}
    except Exception as exc:
        # capturamos algun error inesperado
        registrar_log_notificacion(
            email_cliente,
            services.AsuntosNotificaciones.BIENVENIDA,
            False, 
            f"Excep: {exc}"
        )
        raise
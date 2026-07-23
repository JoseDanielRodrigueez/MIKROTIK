# Tareas asincronas para evitar que la GUI dependa de la respuesta del servidor
# y se bloquee mientras se ejecutan procesos largos
# SOLO ENVIOS ASINCRONOS

from celery import shared_task, Task
from notificaciones.services import AsuntosNotificaciones, enviar_correo, notificar_pago_exitoso, notificar_bienvenida, notificar_suspension, notificar_reconexion
from .logs_utils import registrar_log_notificacion
from datetime import datetime
class RetryTask(Task):
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3, "countdown": 45}


@shared_task(bind=True, base=RetryTask, name='notificaciones.enviar_correo')
def enviar_correo_task(self, email_cliente, asunto, mensaje, remitente=None):
    """Gestiona la tarea asincrona para enviar un correo generico"""
    try:
        if not email_cliente or not email_cliente.strip():
            return 'Email invalido'
        
        exito = enviar_correo(
            email_cliente, 
            asunto, 
            mensaje, 
            remitente
        )

        return {"status": "OK" if exito else "FAILED"}
    except Exception as exc:
        raise


@shared_task(bind=True, base=RetryTask, name='notificaciones.notificar_pago_exitoso')
def pago_exitoso_task(self, email_cliente, nombre_cliente, monto, pendiente, fecha:datetime):
    """Gestiona la tarea asincrona para notificar el pgo exitoso"""
    try:
        if not email_cliente or not email_cliente.strip():
            return 'Email invalido'
        
        exito = notificar_pago_exitoso(
            nombre_cliente, email_cliente, 
            monto, 
            pendiente, 
            fecha
        )

        registrar_log_notificacion(
            email_cliente, 
            AsuntosNotificaciones.PAGO_EXITOSO, 
            exito
        )

        return {"status": "OK" if exito else "FAILED"}
    
    except Exception as exc:
        # capturamos algun error inesperado
        registrar_log_notificacion(
            email_cliente,
            AsuntosNotificaciones.PAGO_EXITOSO,
            False, 
            f"Excep: {exc}"
        )
        raise

@shared_task(bind=True, base=RetryTask, name='notificaciones.bienvenida')
def bienvenida_task(self, nombre_cliente, email_cliente, nombre_plan, vel_sub, vel_baj):
    "gestiona la tarea asincrona para notificar la bienvenida al usuario al registrarse"
    try:
        if not email_cliente or not email_cliente.strip():
            return 'Email invalido'
        
        exito = notificar_bienvenida(
            nombre_cliente, 
            email_cliente, 
            nombre_plan, 
            vel_sub, 
            vel_baj
        )

        registrar_log_notificacion(
            email_cliente, 
            AsuntosNotificaciones.BIENVENIDA,
            exito
        )
        return {"status": "OK" if exito else "FAILED"}
    except Exception as exc:
        # capturamos algun error inesperado
        registrar_log_notificacion(
            email_cliente,
            AsuntosNotificaciones.BIENVENIDA,
            False, 
            f"Excep: {exc}"
        )
        raise

@shared_task(bind=True, base=RetryTask, name='notificaciones.notificar_servicio_suspendido')
def servicio_suspendido_task(self, nombre_cliente, email_cliente, nombre_plan, saldo_pendiente):
    """Gestiona la tarea asincrona para notificar al cliente que si servicio se ha suspendido"""
    try:
        if not email_cliente or not email_cliente.strip():
            return 'Email invalido'
        
        exito = notificar_suspension(
            nombre_cliente,
            email_cliente,
            nombre_plan, 
            saldo_pendiente
        )
        registrar_log_notificacion(
            email_cliente,
            AsuntosNotificaciones.SERVICIO_SUSPENDIDO,
            exito
        )
        return {"status": "OK" if exito else "FAILED"}
    except Exception as exc:
        # capturamos algun error inesperado
        registrar_log_notificacion(
            email_cliente,
            AsuntosNotificaciones.SERVICIO_SUSPENDIDO,
            False, 
            f"Excep: {exc}"
        )
        raise

@shared_task(bind=True, base=RetryTask, name='notificaciones.notificar_servicio_reactivado')
def servicio_reactivado_task(self, nombre_cliente, email_cliente):
    "Gestiona la tarea asincrona paraa el notificar al cliente que ha sido reconectado nuevamente"
    try:
        if not email_cliente or not email_cliente.strip():
            return 'Email invalido'
        
        exito = notificar_reconexion(
            nombre_cliente,
            email_cliente
        )
        registrar_log_notificacion(
            email_cliente,
            AsuntosNotificaciones.SERVICIO_REACTIVADO,
            exito
        )
        return {"status": "OK" if exito else "FAILED"}
    except Exception as exc:
        # capturamos algun error inesperado
        registrar_log_notificacion(
            email_cliente,
            AsuntosNotificaciones.SERVICIO_REACTIVADO,
            False, 
            f"Excep: {exc}"
        )
        raise
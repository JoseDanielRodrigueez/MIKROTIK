"""
en este modulo alojamos una capa de servicio que permite centralizar la logica de los logs de los envios de los correos
de esta forma capturamos los resultados d las tareas o envios sincronos de forma generica y sin ensuciar otras capas de servicio
"""
import logging
from django.contrib.auth import get_user_model
from core.models import Logs
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()
_SYSTEM_USER = None

def get_system_user():
    "retorna el usuario 'sistema' cargado, si no existe registra un log y devuelve none"
    global _SYSTEM_USER
    
    if _SYSTEM_USER is None:

        try:
            return User.objects.get(username='Sistema')
        except User.DoesNotExist:
            Logs.objects.create(
                idPersonal = None,
                mensaje = "Error al intentar obtener al usuario 'Sistema', algunos logs no registraran usuario",
                modulo = "Utilidades",
                error = True,
                fecha = timezone.now(),
            )
            _SYSTEM_USER = None

    return _SYSTEM_USER

def registrar_log_notificacion(destinatario, asunto, exito, error_msg=''):
    "Registra el log generico del estatus de una operacion"

    mensaje = (f"""Notificación {'enviada' if exito else 'fallida'} a {destinatario} Asunto: {asunto}. {error_msg}""").strip()

    Logs.objects.create(
        idPersonal = get_system_user(),
        mensaje = mensaje,
        modulo = "Notificaciones",
        error = not exito,
        fecha = timezone.now()
    )
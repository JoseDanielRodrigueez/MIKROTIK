# Logica de construccion de los mensajes y envio asincrono a traves de los tasks

# notificaciones/services.py
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from core.models import Logs

logger = logging.getLogger(__name__)
User = get_user_model()


def get_system_user():
    try:
        return User.objects.get(username='Sistema')
    except User.DoesNotExist:
        logger.warning("Usuario 'Sistema' no existe. Se usará el primer usuario disponible para Logs.")
        return User.objects.first()


def enviar_notificacion(destinatario, asunto, mensaje, remitente=None):
    """
    Envía un correo simple (solo texto) a un destinatario.
    Retorna True si el envío fue exitoso, False en caso contrario.
    """
    if remitente is None:
        remitente = settings.DEFAULT_FROM_EMAIL

    system_user = get_system_user()

    try:
        sent_count = send_mail(
            subject=asunto,
            message=mensaje,
            from_email=remitente,
            recipient_list=[destinatario],
            fail_silently=False,
        )

        if sent_count == 0:
            raise RuntimeError("send_mail devolvió 0; el servidor SMTP no entregó el mensaje.")

        Logs.objects.create(
            idPersonal=system_user,
            mensaje=f"Se notificó al destinatario {destinatario} que su pago fue procesado exitosamente.",
            modulo="Gestion de pagos",
            error=False,
            fecha=timezone.now(),
        )
        return True

    except Exception as e:
        error_message = str(e) or repr(e)
        logger.exception("Falló el envío del correo a %s con asunto %s", destinatario, asunto)
        Logs.objects.create(
            idPersonal=system_user,
            mensaje=f"Error enviando correo a {destinatario} con asunto: {asunto}. Excepción: {error_message}",
            modulo="Gestion de pagos",
            error=True,
            fecha=timezone.now(),
        )
        return False
    
def notificar_pago_exitoso(cliente_email, nombre_cliente, monto, pendiente):
    """
    Construye y envía un correo de notificación de pago exitoso.
    """
    asunto = "Confirmación de pago exitoso"
    mensaje = (
        f"{_presentacion(nombre_cliente)}"
        f"Su pago de {monto}$ ha sido procesado exitosamente. Ud tiene un saldo pendiente de {pendiente}$.\n"
        "\n\nGracias por preferir nuestros servicios."
    )
    return enviar_notificacion(cliente_email, asunto, mensaje)

def _presentacion(nombre_cliente=None):
    """
    Retorna una cadena de presentación para los correos electrónicos.
    """
    if nombre_cliente:
        return f"Saludos cordiales, {nombre_cliente}\nEl equipo de soporte de la empresa MikroCore le informa que:\n\n"
    return "Saludos cordiales, \nEl equipo de soporte de la empresa MikroCore le informa que:\n\n"
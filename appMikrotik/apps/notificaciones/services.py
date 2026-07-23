import logging
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime
# En esta capa de servicio se aloja la logica de negocio y envio de correo de forma sincrona

logger = logging.getLogger(__name__)

class AsuntosNotificaciones():
    "define constantes para mantener los asuntos de los correos"
    PAGO_EXITOSO = "Confirmacion de pago aprobado"
    BIENVENIDA = "Bienvenido a MikroCore, subcripcion activa"
    SERVICIO_SUSPENDIDO = "MikroCore, servicio suspendido"
    SERVICIO_REACTIVADO = "MikroCore, servicio reactivado"

# METODOS REUTILZABLES

def enviar_correo(destinatario, asunto, mensaje, remitente = None):
    """
    Envia un correo electronico de forma sincrona.
    Retorna True si fue exitoso, en caso contrario False
    """
    
    remitente = remitente or settings.DEFAULT_FROM_EMAIL

    try:
        
        result = send_mail(
            subject = asunto,
            message = mensaje,
            from_email = remitente,
            recipient_list = [destinatario],
            fail_silently = False,
        )

        if result == 0:
            logger.warning(f"Respuesta de send_email = 0 para {destinatario} con asunto {asunto}, posible rechazo del servidor SMTP")
            return False
        
        logger.info(f"Correo enviado exitosamente al destinatario {destinatario}")
        return True

    # capturamos cualquier error desconocido
    except Exception as e:
        error_message = str(e) or repr(e)
        logger.exception(f"Falló el envío del correo a {destinatario} con asunto {asunto}\n\nExcepcion: {error_message}")
        return False
    
def _construir_mensaje(nombre_cliente, cuerpo_mensaje):
    """
    este metodo es un formateador para envolver el cuerpo del mensaje decorandolo con la presentacion dirigida al cliente y pie
    No es necesario colocarle saltos de linea arriba o abajo del mensaje, el envoltorio lo incluye
    """
 
    return f"""Saludos cordiales, {nombre_cliente}. El equipo de MikroCore se dirige a usted para informarle que:

{cuerpo_mensaje}

Si cree que esto es un error contacte a nuestro personal e informe inmediatamente. 
Att: MikroCore. Gracias por preferir nuestros servicios!
"""

#METODOS PERSONALIZADOS 
def notificar_pago_exitoso(nombre_cliente, cliente_email, monto, pendiente, fecha:datetime):
    """
    construye y envia la notificacion de pago exitoso al usuario por su email
    """

    asunto = AsuntosNotificaciones.PAGO_EXITOSO
    mensaje = _construir_mensaje(
        nombre_cliente,
        f"""Su pago realizado por un monto de {monto}$ ha sido procesado exitosamente por nuestro equipo.
Usted cuenta con un saldo pendiente de {pendiente}$
Fecha: {fecha.strftime("%d/%m/%Y %I:%M:%S %p")}"""
    )
        
    return enviar_correo(cliente_email, asunto, mensaje)

def notificar_bienvenida(nombre_cliente, email_cliente, nombre_plan, vel_subida, vel_bajada):
    "Construye y envia el mensaje de bienvenida al usuario"
    asunto = AsuntosNotificaciones.BIENVENIDA
    mensaje = _construir_mensaje(
        nombre_cliente,
        f"""Su subscripcion a nuestros servicios se encuentra activa.
Usted ha adquirido el Plan {nombre_plan} que cuenta con una Velocidad de Subida de {vel_subida} Mpbs (Enviar archivos y subir informacion) y {vel_bajada} Mbps de bajada (para descargas y ver contenido)
Agradecemos su confianza y le damos la mejor bienvenida. Disfrute de su servicio!"""
    )
    
    return enviar_correo(email_cliente, asunto, mensaje)

def notificar_suspension(nombre_cliente, email_cliente, nombre_plan, pendiente):
    "Construye y envia el mensaje de suspension de servicio"
    asunto = AsuntosNotificaciones.SERVICIO_SUSPENDIDO
    mensaje = _construir_mensaje(
        nombre_cliente,
        f"""Su subscripcion a nuestros servicios ha sido suspendida debido a que no ha cancelado el monto mensual de su plan contratado.
Le recordamos que ud tiene contratado el plan {nombre_plan}, debe cancelar {pendiente}$ para seguir disfrutando de nuestro servicios."""
    )

    return enviar_correo(email_cliente, asunto, mensaje)

def notificar_reconexion(nombre_cliente, email_cliente):
    "Construye y envia el mensaje de reconexion de servicio"
    asunto = AsuntosNotificaciones.SERVICIO_REACTIVADO
    mensaje = _construir_mensaje(
        nombre_cliente,
        f"""Su subscripcion a nuestros servicios ha sido reactivada exitosamente!
Esperamos que disfrute su servicio y no dude en contactar con nuestro equipo de soporte en caso de cualquier inconveniente."""
    )

    return enviar_correo(email_cliente, asunto, mensaje)
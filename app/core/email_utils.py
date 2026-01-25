import ssl

def enviar_email(destino: str, asunto: str, mensaje: str) -> bool:
    """
    Envía un correo usando Gmail SMTP con SSL.
    Requiere variables de entorno: GMAIL_USER, GMAIL_PASSWORD
    """
    import os
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_PASSWORD")
    if not user or not password:
        raise Exception("Faltan credenciales de Gmail en variables de entorno")
    msg = MIMEMultipart()
    msg["From"] = user
    msg["To"] = destino
    msg["Subject"] = asunto
    msg.attach(MIMEText(mensaje, "html"))
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(user, password)
            server.sendmail(user, destino, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL] Error enviando correo: {e}")
        return False
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Configuración desde variables de entorno o .env
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_HOST_USER)


def send_recovery_email(to_email: str, token: str):
    subject = "Recuperación de contraseña"
    body = f"""
    Hola,

    Has solicitado restablecer tu contraseña. Utiliza el siguiente token para continuar con el proceso:

    TOKEN: {token}

    Si no solicitaste este cambio, ignora este correo.

    Saludos,
    Soporte
    """
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False

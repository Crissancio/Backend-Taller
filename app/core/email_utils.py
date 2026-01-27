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
    import datetime
    subject = "Recuperación de contraseña"
    now = datetime.datetime.now()
    fecha = now.strftime('%d/%m/%Y')
    hora = now.strftime('%H:%M:%S')
    # Intentar obtener IP pública (si está en contexto web)
    ip = None  # No se obtiene IP aquí, pero se deja el campo

    # HTML amigable y profesional
    body = f"""
    <div style='font-family: Arial, sans-serif; background: #f7f7f7; padding: 32px;'>
      <div style='max-width: 480px; margin: auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #0001; padding: 32px;'>
        <h2 style='color: #2d7ff9; margin-bottom: 8px;'>Recuperación de contraseña</h2>
        <p style='color: #333;'>Hola,</p>
        <p style='color: #333;'>Has solicitado restablecer tu contraseña en <b>Backend-Taller</b>.</p>
        <p style='color: #333;'>Utiliza el siguiente token para continuar con el proceso:</p>
        <div style='margin: 24px 0; text-align: center;'>
          <div style='font-size: 1.3em; background: #f2f6fa; border: 1px solid #2d7ff9; border-radius: 8px; padding: 16px 8px; display: inline-block; word-break: break-all; user-select: all; color: #222; margin-bottom: 8px;'>
            {token}
          </div>
          <div style='color: #666; font-size: 0.98em; margin-top: 6px;'>Selecciona y copia el token manualmente.</div>
        </div>
        <ul style='color: #555; font-size: 0.95em; background: #f2f6fa; border-radius: 6px; padding: 12px 18px;'>
          <li><b>Correo destino:</b> {to_email}</li>
          <li><b>Fecha:</b> {fecha}</li>
          <li><b>Hora:</b> {hora}</li>
          <li><b>IP de solicitud:</b> {ip}</li>
        </ul>
        <p style='color: #888; font-size: 0.95em; margin-top: 18px;'>Si no solicitaste este cambio, puedes ignorar este correo.</p>
        <p style='color: #2d7ff9; font-size: 1.1em; margin-top: 24px;'>Equipo Backend-Taller</p>
      </div>
    </div>
    """
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False
